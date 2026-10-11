// Package lifecycle demonstrates bounded, cooperative task ownership, not a production queue.
package lifecycle

import (
    "context"
    "errors"
    "sync"
)

const MaxInputs = 4096

// Map returns ordered complete results, or an error without partial results.
// fn must return when its context is cancelled and must not panic.
// Cancellation is cooperative: Map joins every owned goroutine before returning.
func Map(ctx context.Context, workers int, input []int, fn func(context.Context, int) (int, error)) ([]int, error) {
    if ctx == nil || fn == nil || workers < 1 || workers > 64 || len(input) > MaxInputs {
        return nil, errors.New("invalid teaching pool parameters")
    }
    if err := ctx.Err(); err != nil { return nil, err }
    if len(input) == 0 { return []int{}, nil }
    if workers > len(input) { workers = len(input) }
    child, cancel := context.WithCancel(ctx)
    defer cancel()
    jobs := make(chan int) // feeder owns close; workers only receive
    output := make([]int, len(input))
    var joined sync.WaitGroup
    var first sync.Once
    var firstErr error
    joined.Add(workers + 1)
    for worker := 0; worker < workers; worker++ {
        go func() {
            defer joined.Done()
            for {
                select {
                case <-child.Done(): return
                case index, ok := <-jobs:
                    if !ok { return }
                    // select has no cancellation priority; avoid knowingly starting expired work.
                    if child.Err() != nil { return }
                    value, err := fn(child, input[index])
                    if err != nil {
                        first.Do(func() { firstErr = err; cancel() })
                        return
                    }
                    output[index] = value // each index has exactly one writer
                }
            }
        }()
    }
    go func() {
        defer joined.Done()
        defer close(jobs)
        for index := range input {
            select {
            case <-child.Done(): return
            case jobs <- index:
            }
        }
    }()
    joined.Wait() // includes feeder, not just computation workers
    if firstErr != nil { return nil, firstErr }
    if err := ctx.Err(); err != nil { return nil, err }
    return output, nil
}
