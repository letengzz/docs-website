# 异步函数

在ES7中，异步函数被引入，允许使用async和await关键字来编写异步代码。这个特性使异步编程更加容易和直观。

## async 函数

async 函数返回值为Promise对象，Promise对象的结果由async函数执行的返回值决定。

```javascript
async funcation main(){
    //1. 如果返回值是一个非Promise类型的数据
    // return 521;
    //2. 如果返回的是一个Promise对象
    //return new Promise((resolve,reject) =>{
    //    reject('Error');
    //})
    //3. 抛出异常
    throw 'Error';
}

let result = main();

console.log(result);
```

## await 表达式

await 右侧的表达式一般为Promise对象，但也可以是其它的值。如果表达式是Promise对象，await返回的是Promise成功的值。如果表达式是其它值，直接将此值作为await的返回值。

:::warning 说明

- await 必须写在async函数中，但也可以是其它的值。
- 如果await的Promise失败了，就会抛出异常，需要通过 try...catch 捕获处理。

:::

```javascript
async funcation main(){
    let p = new Promise((resolve,reject) =>{
        reject('Error');
    })
    //1. 右侧为Promise
    let res = await p;
    //2. 右侧为其他类型的数据
    let res2 = await 20;
  	//3. 如果Promise是失败的状态
    try{
        let res3 = await p;
    }catch(e){
        console.log(e);
    }
}
```
