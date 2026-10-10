package cancellation

import (
	"bufio"
	"bytes"
	"context"
	"errors"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"sync/atomic"
	"testing"
	"time"
)

const exitBound = 2 * time.Second

func bounded(t *testing.T, f func() error) error {
	t.Helper()
	result := make(chan error, 1)
	go func() { result <- f() }()
	select {
	case err := <-result:
		return err
	case <-time.After(exitBound):
		t.Fatal("fixture did not return within its cleanup bound")
		return nil
	}
}

func inputValues() []int {
	values := make([]int, 100)
	for i := range values {
		values[i] = i
	}
	return values
}

func TestPipelineNormalAndSlowConsumer(t *testing.T) {
	for _, slow := range []bool{false, true} {
		t.Run(map[bool]string{false: "normal", true: "slow_consumer"}[slow], func(t *testing.T) {
			seen := make(map[int]bool)
			var entered, exited atomic.Int64
			err := bounded(t, func() error {
				return RunPipeline(context.Background(), inputValues(), 4, 2,
					func(ctx context.Context, v int) (int, error) {
						entered.Add(1)
						defer exited.Add(1)
						return v * v, ctx.Err()
					}, func(ctx context.Context, v int) error {
						if slow {
							timer := time.NewTimer(time.Millisecond)
							defer timer.Stop()
							select {
							case <-ctx.Done():
								return ctx.Err()
							case <-timer.C:
							}
						}
						if seen[v] {
							return errors.New("duplicate output")
						}
						seen[v] = true
						return nil
					})
			})
			if err != nil || len(seen) != 100 || entered.Load() != exited.Load() {
				t.Fatalf("err=%v outputs=%d callbacks=%d/%d", err, len(seen), entered.Load(), exited.Load())
			}
		})
	}
}

func TestPipelineEarlyConsumerExit(t *testing.T) {
	for _, buffer := range []int{0, 2} {
		var entered, exited atomic.Int64
		err := bounded(t, func() error {
			return RunPipeline(context.Background(), inputValues(), 4, buffer,
				func(ctx context.Context, v int) (int, error) {
					entered.Add(1)
					defer exited.Add(1)
					return v, ctx.Err()
				}, func(context.Context, int) error { return ErrStop })
		})
		if err != nil || entered.Load() != exited.Load() {
			t.Fatalf("buffer=%d err=%v callbacks=%d/%d", buffer, err, entered.Load(), exited.Load())
		}
	}
}

func TestPipelineWorkerFailure(t *testing.T) {
	failure := errors.New("synthetic worker failure")
	var entered, exited atomic.Int64
	err := bounded(t, func() error {
		return RunPipeline(context.Background(), inputValues(), 4, 0,
			func(ctx context.Context, v int) (int, error) {
				entered.Add(1)
				defer exited.Add(1)
				if v == 7 {
					return 0, failure
				}
				return v, ctx.Err()
			}, func(context.Context, int) error { return nil })
	})
	if !errors.Is(err, failure) || entered.Load() != exited.Load() {
		t.Fatalf("err=%v callbacks=%d/%d", err, entered.Load(), exited.Load())
	}
}

func TestPipelineConsumerFailure(t *testing.T) {
	failure := errors.New("synthetic consumer failure")
	err := bounded(t, func() error {
		return RunPipeline(context.Background(), inputValues(), 4, 0,
			func(ctx context.Context, v int) (int, error) { return v, ctx.Err() },
			func(context.Context, int) error { return failure })
	})
	if !errors.Is(err, failure) {
		t.Fatalf("consumer error was not preserved: %v", err)
	}
}

func TestPipelineCancelDuringWork(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	started := make(chan struct{}, 4)
	var entered, exited atomic.Int64
	result := make(chan error, 1)
	go func() {
		result <- RunPipeline(ctx, inputValues(), 4, 0,
			func(ctx context.Context, v int) (int, error) {
				entered.Add(1)
				defer exited.Add(1)
				started <- struct{}{}
				<-ctx.Done()
				return 0, ctx.Err()
			}, func(context.Context, int) error { return nil })
	}()
	select {
	case <-started:
		cancel()
	case <-time.After(exitBound):
		t.Fatal("no worker started")
	}
	select {
	case err := <-result:
		if !errors.Is(err, context.Canceled) || entered.Load() != exited.Load() {
			t.Fatalf("err=%v callbacks=%d/%d", err, entered.Load(), exited.Load())
		}
	case <-time.After(exitBound):
		t.Fatal("producer/workers did not join after cancellation")
	}
}

// fakeWriter isolates blocked writes and disconnected clients without sockets.
// It is owned by the single handler goroutine; tests read it after that goroutine joins.
type fakeWriter struct {
	header http.Header
	body bytes.Buffer
	deadline time.Time
	blocked bool
	disconnected bool
	flushes int
}

func (w *fakeWriter) Header() http.Header { return w.header }
func (w *fakeWriter) WriteHeader(int) {}
func (w *fakeWriter) SetWriteDeadline(deadline time.Time) error {
	w.deadline = deadline
	return nil
}
func (w *fakeWriter) Write(p []byte) (int, error) {
	if w.disconnected {
		return 0, io.ErrClosedPipe
	}
	if w.blocked {
		if w.deadline.IsZero() {
			return 0, errors.New("write deadline was not set")
		}
		timer := time.NewTimer(time.Until(w.deadline))
		defer timer.Stop()
		<-timer.C
		return 0, os.ErrDeadlineExceeded
	}
	return w.body.Write(p)
}
func (w *fakeWriter) FlushError() error { w.flushes++; return nil }

func TestSSENormalFailureSlowAndDisconnected(t *testing.T) {
	for _, tc := range []struct {
		name string
		blocked, disconnected bool
		failAt int
		want error
		wantBody string
	}{
		{"normal", false, false, -1, nil, "data: a\n\ndata: b\n\n"},
		{"model_failure", false, false, 1, ErrModel, "data: a\n\n"},
		{"slow_reader", true, false, -1, os.ErrDeadlineExceeded, ""},
		{"disconnected_writer", false, true, -1, io.ErrClosedPipe, ""},
	} {
		t.Run(tc.name, func(t *testing.T) {
			w := &fakeWriter{header: make(http.Header), blocked: tc.blocked, disconnected: tc.disconnected}
			err := bounded(t, func() error {
				return StreamSSE(context.Background(), w, []string{"a", "b"}, 0, 20*time.Millisecond, tc.failAt)
			})
			if !errors.Is(err, tc.want) || w.body.String() != tc.wantBody {
				t.Fatalf("err=%v body=%q", err, w.body.String())
			}
			if tc.want == nil && (w.flushes != 2 || !w.deadline.IsZero()) {
				t.Fatalf("flush count=%d remaining deadline=%v", w.flushes, w.deadline)
			}
		})
	}
}

func TestSSEFirstTokenDeadlineAndUnsupportedWriter(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Millisecond)
	defer cancel()
	w := &fakeWriter{header: make(http.Header)}
	err := bounded(t, func() error {
		return StreamSSE(ctx, w, []string{"a"}, time.Hour, time.Second, -1)
	})
	if !errors.Is(err, context.DeadlineExceeded) || w.body.Len() != 0 {
		t.Fatalf("err=%v bytes=%d", err, w.body.Len())
	}
	err = StreamSSE(context.Background(), httptest.NewRecorder(), []string{"a"}, 0, time.Second, -1)
	if !errors.Is(err, http.ErrNotSupported) {
		t.Fatalf("unsupported deadline writer: %v", err)
	}
}

func TestSSEClientDisconnectCancelsHandler(t *testing.T) {
	done := make(chan error, 1)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// A first token enables a deterministic client disconnect. The next
		// token's long wait must end through request-context cancellation.
		if err := StreamSSE(r.Context(), w, []string{"first"}, 0, time.Second, -1); err != nil {
			done <- err
			return
		}
		done <- StreamSSE(r.Context(), w, []string{"second"}, time.Hour, time.Second, -1)
	}))
	ctx, cancel := context.WithCancel(context.Background())
	defer func() {
		cancel()
		server.CloseClientConnections()
		server.Close()
	}()
	client := server.Client()
	client.Timeout = 0 // No competing timeout may cause the observed cancellation.
	request, err := http.NewRequestWithContext(ctx, http.MethodGet, server.URL, nil)
	if err != nil {
		t.Fatal(err)
	}
	type responseResult struct {
		response *http.Response
		err error
	}
	responses := make(chan responseResult, 1)
	go func() {
		response, err := client.Do(request)
		responses <- responseResult{response, err}
	}()
	var response *http.Response
	select {
	case got := <-responses:
		if got.err != nil {
			t.Fatal(got.err)
		}
		response = got.response
	case <-time.After(exitBound):
		t.Fatal("response headers did not arrive within the observation bound")
	}
	defer response.Body.Close()
	type tokenResult struct {
		text string
		ok bool
		err error
	}
	tokens := make(chan tokenResult, 1)
	go func() {
		scanner := bufio.NewScanner(response.Body)
		ok := scanner.Scan()
		tokens <- tokenResult{scanner.Text(), ok, scanner.Err()}
	}()
	select {
	case got := <-tokens:
		if !got.ok || got.text != "data: first" {
			t.Fatalf("first token missing: %v", got.err)
		}
	case <-time.After(exitBound):
		t.Fatal("first token did not arrive within the observation bound")
	}
	// cancel() is deliberately deferred until after this observation. Only
	// closing the unfinished response body should make the server context end.
	if err := response.Body.Close(); err != nil {
		t.Fatal(err)
	}
	select {
	case err := <-done:
		if !errors.Is(err, context.Canceled) {
			t.Fatalf("handler result=%v", err)
		}
	case <-time.After(exitBound):
		t.Fatal("HTTP handler did not exit after client disconnected")
	}
}
