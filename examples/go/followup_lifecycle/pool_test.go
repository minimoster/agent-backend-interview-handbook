package lifecycle

import (
    "context"
    "errors"
    "reflect"
    "sync/atomic"
    "testing"
    "time"
)

func twice(_ context.Context, n int) (int, error) { return n*2, nil }
func waitResult(t *testing.T, result <-chan error) error {
    t.Helper()
    select { case err := <-result: return err; case <-time.After(3*time.Second): t.Fatal("owned work did not finish"); return nil }
}
func TestInvalidWorkers(t *testing.T) {
    for _, n := range []int{-1,0,65} { if _,err:=Map(context.Background(),n,[]int{1},twice);err==nil {t.Fatalf("accepted %d",n)} }
}
func TestInvalidDependencies(t *testing.T) {
    if _,err:=Map(nil,1,[]int{1},twice);err==nil {t.Fatal("accepted nil context")}
    if _,err:=Map(context.Background(),1,[]int{1},nil);err==nil {t.Fatal("accepted nil callback")}
}
func TestInputBound(t *testing.T) {
    if _,err:=Map(context.Background(),1,make([]int,MaxInputs+1),twice);err==nil {t.Fatal("unbounded input accepted")}
}
func TestOrderedCompleteResults(t *testing.T) {
    for _,workers:=range []int{1,2,64} {
        output,err:=Map(context.Background(),workers,[]int{9,1,5,2},twice)
        if err!=nil || !reflect.DeepEqual(output,[]int{18,2,10,4}) {t.Fatalf("%v %v",output,err)}
    }
}
func TestEmptyResults(t *testing.T) {
    output,err:=Map(context.Background(),2,nil,twice)
    if err!=nil || len(output)!=0 || output==nil {t.Fatalf("%v %v",output,err)}
}
func TestAlreadyCancelledDoesNotStart(t *testing.T) {
    ctx,cancel:=context.WithCancel(context.Background());cancel()
    var calls atomic.Int32
    output,err:=Map(ctx,2,[]int{1,2},func(context.Context,int)(int,error){calls.Add(1);return 1,nil})
    if !errors.Is(err,context.Canceled)||output!=nil||calls.Load()!=0 {t.Fatalf("%v %v %d",output,err,calls.Load())}
}
func TestCancellationJoinsCooperativeWorkers(t *testing.T) {
    ctx,cancel:=context.WithCancel(context.Background());defer cancel()
    started:=make(chan struct{},1);result:=make(chan error,1);var active atomic.Int32
    go func(){_,err:=Map(ctx,1,[]int{1,2,3},func(child context.Context,_ int)(int,error){
        active.Add(1);defer active.Add(-1);started<-struct{}{};<-child.Done();return 0,child.Err()
    });result<-err}()
    select {case <-started:case <-time.After(3*time.Second):t.Fatal("worker did not start")}
    cancel()
    if err:=waitResult(t,result);!errors.Is(err,context.Canceled)||active.Load()!=0 {t.Fatalf("%v %d",err,active.Load())}
}
func TestErrorHasNoPartialResult(t *testing.T) {
    expected:=errors.New("synthetic failure")
    output,err:=Map(context.Background(),1,[]int{1,2,3},func(_ context.Context,n int)(int,error){if n==2{return 0,expected};return n,nil})
    if !errors.Is(err,expected)||output!=nil {t.Fatalf("%v %v",output,err)}
}
func TestActiveConcurrencyBound(t *testing.T) {
    const workers=4
    ctx,cancel:=context.WithCancel(context.Background());defer cancel()
    gate:=make(chan struct{});started:=make(chan struct{},workers);result:=make(chan error,1)
    var active,maximum,total atomic.Int32
    go func(){_,err:=Map(ctx,workers,make([]int,100),func(child context.Context,n int)(int,error){
        current:=active.Add(1);defer active.Add(-1)
        for {old:=maximum.Load();if current<=old||maximum.CompareAndSwap(old,current){break}}
        if total.Add(1)<=workers {started<-struct{}{}}
        select {case <-gate:return n,nil;case <-child.Done():return 0,child.Err()}
    });result<-err}()
    for i:=0;i<workers;i++ {select {case <-started:case <-time.After(3*time.Second):cancel();t.Fatal("workers did not enter")}}
    close(gate)
    if err:=waitResult(t,result);err!=nil||maximum.Load()!=workers||active.Load()!=0 {t.Fatalf("%v max=%d active=%d",err,maximum.Load(),active.Load())}
}
func TestRepeatedCompletionAndFailure(t *testing.T) {
    for i:=0;i<200;i++ {
        _,err:=Map(context.Background(),3,[]int{1,2,3},twice);if err!=nil {t.Fatal(err)}
        _,err=Map(context.Background(),3,[]int{1,2,3},func(context.Context,int)(int,error){return 0,errors.New("failure")})
        if err==nil {t.Fatal("lost failure")}
    }
}
