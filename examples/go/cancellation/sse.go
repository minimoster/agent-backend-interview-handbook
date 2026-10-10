package cancellation

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"strings"
	"time"
)

var ErrModel = errors.New("synthetic model failure")

// StreamSSE is a fake model stream invoked inside an HTTP handler. failAt=-1
// disables failure injection; otherwise it fails before token failAt. The writer
// must support write deadlines and flushing: unsupported wrappers fail explicitly.
// This fixture owns response write deadlines and clears them after each flush.
// A finite per-write budget bounds slow-reader stalls; request cancellation alone
// does not necessarily interrupt a Write already in progress.
func StreamSSE(ctx context.Context, w http.ResponseWriter, tokens []string,
	gap, writeBudget time.Duration, failAt int) error {
	if gap < 0 || writeBudget <= 0 || failAt < -1 {
		return fmt.Errorf("invalid stream configuration")
	}
	control := http.NewResponseController(w)
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	for i, token := range tokens {
		if err := ctx.Err(); err != nil {
			return err
		}
		if gap > 0 {
			timer := time.NewTimer(gap)
			select {
			case <-ctx.Done():
				timer.Stop()
				return ctx.Err()
			case <-timer.C:
			}
		}
		// The timer and cancellation can become ready together. Recheck
		// after the gap rather than interpreting a timer wakeup as permission.
		if err := ctx.Err(); err != nil {
			return err
		}
		if i == failAt {
			return ErrModel
		}
		if err := control.SetWriteDeadline(time.Now().Add(writeBudget)); err != nil {
			return err
		}
		// Split multiline data into valid SSE data fields; do not emit raw CR.
		token = strings.ReplaceAll(strings.ReplaceAll(token, "\r", ""), "\n", "\ndata: ")
		if _, err := fmt.Fprintf(w, "data: %s\n\n", token); err != nil {
			return err
		}
		if err := control.Flush(); err != nil {
			return err
		}
		// Do not leave this deadline armed while waiting for the next token.
		// An already exceeded write deadline cannot be extended to recover it.
		if err := control.SetWriteDeadline(time.Time{}); err != nil {
			return err
		}
	}
	return ctx.Err()
}
