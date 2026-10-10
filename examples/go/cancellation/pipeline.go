// Package cancellation contains synthetic teaching fixtures, not production handlers.
package cancellation

import (
	"context"
	"errors"
	"fmt"
	"sync"
)

// ErrStop lets the serial consumer stop successfully after receiving enough values.
var ErrStop = errors.New("consumer has enough values")

// RunPipeline joins its producer, workers and result closer before returning.
// Callbacks must not panic and must return when ctx is canceled. Cancellation
// cannot forcibly stop a callback that ignores its context. Results are unordered.
func RunPipeline(parent context.Context, input []int, workers, buffer int,
	work func(context.Context, int) (int, error),
	consume func(context.Context, int) error) error {
	if workers < 1 || buffer < 0 || work == nil || consume == nil {
		return fmt.Errorf("invalid pipeline configuration")
	}
	ctx, cancel := context.WithCancel(parent)
	defer cancel()
	jobs := make(chan int, buffer)
	results := make(chan int, buffer)
	done := make(chan struct{})
	var wg sync.WaitGroup
	var once sync.Once
	var firstErr error
	fail := func(err error) {
		once.Do(func() {
			firstErr = err
			cancel()
		})
	}
	// Register all tasks before the closer can call Wait.
	wg.Add(1 + workers)
	go func() {
		defer wg.Done()
		defer close(jobs) // Only the producer closes jobs.
		for _, value := range input {
			select {
			case <-ctx.Done():
				return
			case jobs <- value:
			}
		}
	}()
	for i := 0; i < workers; i++ {
		go func() {
			defer wg.Done()
			for {
				select {
				case <-ctx.Done():
					return
				case value, ok := <-jobs:
					if !ok {
						return
					}
					result, err := work(ctx, value)
					if err != nil {
						fail(err)
						return
					}
					select {
					case <-ctx.Done():
						return
					case results <- result:
					}
				}
			}
		}()
	}
	go func() {
		wg.Wait()
		close(results) // No worker can send after this point.
		close(done)
	}()
	var consumerErr error
consumeLoop:
	for {
		select {
		case <-ctx.Done():
			break consumeLoop
		case value, ok := <-results:
			if !ok {
				break consumeLoop
			}
			if err := consume(ctx, value); err != nil {
				consumerErr = err
				break consumeLoop
			}
		}
	}
	cancel() // Also unblocks sends when the consumer ends early.
	<-done
	// Reading firstErr is safe after the join, even when no consumer saw a result.
	if errors.Is(consumerErr, ErrStop) {
		return nil
	}
	if consumerErr != nil {
		return consumerErr
	}
	if firstErr != nil {
		return firstErr
	}
	return parent.Err()
}
