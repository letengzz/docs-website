# JUC并发编程

### 相关概念

> 进程
>
> 是程序的一次执行，是系统进行资源分配和调度的独立单位，每个进程都有它自己的内存空间和系统资源

> 线程
>
> 在同一进程内又可以执行多个任务，这样的任务可以看做是线程
>
> 一个进程会有1个或多个线程

> 管程
>
> Monitor（监视器），也就是平时说的锁

> Java线程分为用户线程和守护线程
>
> 线程的daemon属性为true表示是守护线程，false表示是用户线程
>
> 用户线程
>
> 是一种特殊的线程，在后台默默地完成一些系统性的服务，比如垃圾回收线程

> 守护线程
>
> 是系统的工作线程，会完成这个程序需要完成的业务操作

### CompletableFuture

> Future接口和Callable接口
>
> Future接口定义了操作异步任务执行一些方法，如获取异步任务的执行结果，取消任务的执行，判断任务是否完毕等。
>
> Callable接口中定义了需要有返回的任务需要实现的方法

#### **FutureTask的用法**

get() 阻塞，一旦调用get()方法，不管是否计算完成都会导致阻塞

isDone()轮询，轮询的方式会耗费无谓的CPU资源，而且不见得能及时得到计算结果；如果想要异步获取结果，通常都会以轮询的方式去获取结果，尽量不要阻塞。

#### **CompleableFuture**

- 在Java8中，CompletableFuture提供了非常强大的Future的扩展功能，可以简化异步编程的复杂性，并提供了函数式编程的能力，可以通过回调处理计算结果，也提供了转换和组合CompletableFuture的方法。

- 它可能代表一个明确完成的Future，也有可能代表一个完成阶段（CompletionStage），它支持在计算完成以后触发一些函数或执行某些动作。

- 类结构：`public class CompletableFuture<T> implements Future<T>, CompletionStage<T> `

CompletionStage代表异步计算过程中的某一阶段，一个阶段完成以后可能会触发另外一个阶段（有点类似Linux中的管道符）

一个阶段的执行可能是被单个阶段的完成触发，也可能是由多个阶段一起触发

#### CompletableFuture常用API

**创建异步对象**

```java
public static CompletableFuture<Void> runAsync(Runnable runnable)
public static CompletableFuture<Void> runAsync(Runnable runnable, Executor executor)
public static <U> CompletableFuture<U> supplyAsync(Supplier<U> supplier)
public static <U> CompletableFuture<U> supplyAsync(Supplier<U> supplier, Executor executor)
```

1、runXxxx都是没有返回结果的，supplyXxx都是可以获取返回结果的

2、可以传入自定义的线程池，否则就用默认的线程池；

**计算完成时回调方法**

```java
public CompletableFuture<T> whenComplete(BiConsumer<? super T, ? super Throwable> action)
public CompletableFuture<T> whenCompleteAsync(BiConsumer<? super T, ? super Throwable> action)    
public CompletableFuture<T> whenCompleteAsync(BiConsumer<? super T, ? super Throwable> action, Executor executor)    

public CompletableFuture<T> exceptionally(Function<Throwable, ? extends T> fn)
```

whenComplete可以感知正常和异常的计算结果，但是没有返回值；exceptionally处理异常情况，并且有返回值。

whenComplete和whenCompleteAsync的区别： 

- whenComplete：是执行当前任务的线程执行继续执行whenComplete的任务。 
- whenCompleteAsync：是执行把whenCompleteAsync这个任务继续提交给线程池来进行执行。

方法不以Async结尾，意味着Action使用相同的线程执行，而Async可能会使用其他线程执行（如果是使用相同的线程池，也可能会被同一个线程选中执行）

**handle 方法**

```java
public <U> CompletableFuture<U> handle(BiFunction<? super T, Throwable, ? extends U> fn) 
public <U> CompletableFuture<U> handleAsync(BiFunction<? super T, Throwable, ? extends U> fn)
public <U> CompletableFuture<U> handleAsync(BiFunction<? super T, Throwable, ? extends U> fn, Executor executor)

```

和complete 一样，可对结果做最后的处理（可处理异常），可改变返回值。



**线程串行化方法**

```java
public <U> CompletableFuture<U> thenApply(Function<? super T,? extends U> fn)
public <U> CompletableFuture<U> thenApplyAsync(Function<? super T,? extends U> fn)
public <U> CompletableFuture<U> thenApplyAsync(Function<? super T,? extends U> fn, Executor executor)
    
public CompletableFuture<Void> thenAccept(Consumer<? super T> action)
public CompletableFuture<Void> thenAcceptAsync(Consumer<? super T> action)
public CompletableFuture<Void> thenAcceptAsync(Consumer<? super T> action, Executor executor)

public CompletableFuture<Void> thenRun(Runnable action)
public CompletableFuture<Void> thenRunAsync(Runnable action)
public CompletableFuture<Void> thenRunAsync(Runnable action, Executor executor)
```

thenApply 方法：当一个线程依赖另一个线程时，获取上一个任务返回的结果，并返回当前任务的返回值。 

thenAccept 方法：消费处理结果。接收任务的处理结果，并消费处理，无返回结果。 

thenRun 方法：只要上面的任务执行完成，就开始执行thenRun，只是处理完任务后，执行thenRun 的后续操作 

带有Async 默认是异步执行的。

同之前。 以上都要前置任务成功完成。 

Function 

- T：上一个任务返回结果的类型
- U：当前任务的返回值类型

**两任务组合- 都要完成**

```java
public <U,V> CompletableFuture<V> thenCombine(CompletionStage<? extends U> other,BiFunction<? super T,? super U,? extends V> fn)
public <U,V> CompletableFuture<V> thenCombineAsync(CompletionStage<? extends U> other,BiFunction<? super T,? super U,? extends V> fn)
public <U,V> CompletableFuture<V> thenCombineAsync(CompletionStage<? extends U> other,BiFunction<? super T,? super U,? extends V> fn, Executor executor)

public <U> CompletableFuture<Void> thenAcceptBoth(CompletionStage<? extends U> other,BiConsumer<? super T, ? super U> action)
public <U> CompletableFuture<Void> thenAcceptBothAsync(CompletionStage<? extends U> other,BiConsumer<? super T, ? super U> action)
public <U> CompletableFuture<Void> thenAcceptBothAsync(CompletionStage<? extends U> other,BiConsumer<? super T, ? super U> action, Executor executor)


public CompletableFuture<Void> runAfterBoth(CompletionStage<?> other,Runnable action)
public CompletableFuture<Void> runAfterBothAsync(CompletionStage<?> other,Runnable action)
public CompletableFuture<Void> runAfterBothAsync(CompletionStage<?> other,Runnable action,Executor executor)
```

两任务都要完成，才触发该任务

thenCombine：组合两个 future，获取两个 future 的返回结果，并返回当前任务的返回值

thenAcceptBoth：组合两个 future，获取两个 future 任务的返回结果，然后处理任务，没有返回值。

runAfterBoth：组合两个 future，不需要获取 future 的结果，只需两个 future 处理完任务后，处理该任务。



**两任务组合- 一个完成**

```java
public <U> CompletableFuture<U> applyToEither(CompletionStage<? extends T> other, Function<? super T, U> fn)
public <U> CompletableFuture<U> applyToEitherAsync(CompletionStage<? extends T> other, Function<? super T, U> fn)
public <U> CompletableFuture<U> applyToEitherAsync(CompletionStage<? extends T> other, Function<? super T, U> fn,Executor executor)

public CompletableFuture<Void> acceptEither(CompletionStage<? extends T> other, Consumer<? super T> action)
public CompletableFuture<Void> acceptEitherAsync(CompletionStage<? extends T> other, Consumer<? super T> action)
public CompletableFuture<Void> acceptEitherAsync(CompletionStage<? extends T> other, Consumer<? super T> action,Executor executor)

public CompletableFuture<Void> runAfterEither(CompletionStage<?> other,Runnable action)
public CompletableFuture<Void> runAfterEitherAsync(CompletionStage<?> other,Runnable action)
public CompletableFuture<Void> runAfterEitherAsync(CompletionStage<?> other,Runnable action,Executor executor)
```

当两个任务中，任意一个future任务完成的时候，执行任务。 

applyToEither：两个任务有一个执行完成，获取它的返回值，处理任务并有新的返回值。 

acceptEither：两个任务有一个执行完成，获取它的返回值，处理任务，没有新的返回值。 

runAfterEither：两个任务有一个执行完成，不需要获取future的结果，处理任务，也没有返回值。

**多任务组合**

```java
public static CompletableFuture<Void> allOf(CompletableFuture<?>... cfs)

public static CompletableFuture<Object> anyOf(CompletableFuture<?>... cfs)
```

allOf：等待所有任务完成 

anyOf：只要有一个任务完成
