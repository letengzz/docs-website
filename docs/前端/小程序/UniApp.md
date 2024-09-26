> 使用setTimeout来实现$nextTick()的功能

```javascript
setTimeout(()=>{
  //do something
},0)
```
> 在子组件中使用v-model实现双向数据绑定
> v-model 是vue中完成双向数据绑定的指令，如果说想要应用到组件的绑定中，那么需要遵守以下规则：

1. 子组件中接收到的值必须以value命名
2. 子组件中想要修改value时，必须要发送一个叫做input的事件
3. 满足以上两点，父组件可以通过v-model指令把值直接传递给value这个props
> 在uniapp中使用vuex

```
//在根目录中创建store文件夹，然后创建index.js
//导入Vue和Vuex
import Vue from 'vue'
//uniapp 已默认安装，不需要重新下载
import Vuex from 'vuex'
//安装Vuex插件
Vue.use(Vuex);
//创建store实例
const store = new Vuex.Store({});
export default store;

//在main.js中注册vuex插件
import store from './store';
const app = new Vue({
...App,
store//挂载实例对象
});
app.$mount();

//使用模块
在store文件夹下创建modules文件夹
在下面创建想要的js文件，例如user.js
//在user.js文件中写入
state = () =>{ return {}; }
mutations ={}
actions = {}
export default {  namespaced: true,  state,  mutations,  actions}

//在store下的index.js中写入
import user from './modules/user'
const store = new Vuex.Store({
  modules: {
    user
  }
})

//注意事项
使用state数据
//导入mapState函数
import { mapState } from 'vuex';
//然后在computed中，通过mapState函数，注册state中的数据，导入后的数据可以直接使用
//使用方法： ...mapState( 模块名, ['属性名','属性名','属性名'])
...mapState(user,['name'])
//导入mapMutations函数，可以将mutations中的方法导入到methods中
使用方法：...mapMutations('模块名',['方法名','方法名'])
//导入mapActions函数，可以将actions中的方法导入到methods中
使用方法：...mapActions('模块名',['方法名','方法名'])

mutations中的方法第一个参数是state，之后的参数为形参
例如：
const mutations = {
SET_TOKEN: (state, token) => {
 	state.token = token
 }
}
actions中的方法第一个参数是一个对象，为context，一般写成{ commit, state }，其后为形参
const actions = {
  login({ commit, state }, userInfo) {
 ...
//commit用来调用mutations中的方法
        commit('SET_TOKEN', data.accessToken)
  }
}
调用actions中的方法需要使用dispatch
user/login : user为命名空间名称，login为actions中的方法名
this.$store.dispatch('user/login', this.loginForm)
```

> 在uniapp中使用mescroll实现下拉刷新，上拉加载

```
https://www.mescroll.com/uni.html#begin
```

> uniapp分包

```
分包：将小程序划分为不同的子包，在构建时打包成不同的分包，用户在使用时按需进行加载
步骤：
1. 打开pages.json，新建subPackages节点
2. 节点中每个对象为一个分包，其中
  a. root：分包包名
  b. name：分包别名
  c. pages：分包下的页面
    ⅰ. path：分包下的页面路径
    ⅱ. style：页面的样式
3. 示例：
	"subPackages": [
		{
			"root": "subpkg",
			"name":"sub-1",
			"pages": [
				{
					"path": "pages/test/test",
					"style": {
						"navigationBarTitleText": "测试分包"
					}
				}
			]
		}
	]
4. 注意：页面存放位置在分包包名这个目录下（/subpkg/pages/test/test）
```

