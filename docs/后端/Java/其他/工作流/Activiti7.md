# 知识点
## 部署&定义
### xml文件部署
```java
//key为流程文件中设置的key一般为  *.bpmn20 中的*
Deployment deploy = repositoryService.createDeployment()
    .addClasspathResource("BPMN/qingjia1.bpmn20.xml")
    .name("请假流程1").deploy();
System.out.println(deploy.getId());
System.out.println(deploy.getName());
```
### ZIP文件部署
```java
//先获取ZipInputStream，然后使用RepositoryService部署
try (
        FileInputStream fileInputStream = FileUtils.openInputStream(new File(filePath));
        ZipInputStream zipInputStream = new ZipInputStream(fileInputStream);
     ){
    repositoryService.createDeployment()
            .addZipInputStream(zipInputStream)
            .deploy();
}catch (Exception ex){
    // 手动捕捉异常 可以往大了捕捉，或者在catch的最后添加最大的异常Exception 防止有异常没捕捉到
    //用zip文件部署时，如果文件不符合规定，
    //会报异常ActivitiException: problem reading zip input stream
    log.error("Class:{},msg:{}",ex.getClass(),ex.getMessage());
    throw new CustomException("部署异常，请查看流程文件状态");
}
```
### 部署查询
```java
@Test
public void test2(){
    List<Deployment> list = repositoryService.createDeploymentQuery().list();
    for (Deployment deployment : list) {
        System.out.println("Id："+deployment.getId());
        System.out.println("Name："+deployment.getName());
        System.out.println("Key："+deployment.getKey());
        System.out.println("DeploymentTime："+deployment.getDeploymentTime());
    }
}
```
### 流程定义
```java
//流程定义查询
@Test
public void test1(){
    List<ProcessDefinition> list = repositoryService.createProcessDefinitionQuery().list();
    for (ProcessDefinition pd : list) {
        System.out.println("-----------流程定义：-----------");
        System.out.println("id："+pd.getId());
        System.out.println("key："+pd.getKey());
        System.out.println("name："+pd.getName());
        System.out.println("resourceName："+pd.getResourceName());
        System.out.println("deployment："+pd.getDeploymentId());
        System.out.println("version："+pd.getVersion());
    }
}

//流程定义删除
//根据部署id删除
@Test
public void test2(){
    String deploymentId = "3a6f6182-2693-11ee-856a-4ed577080d8b";
    //第二个参数为true  则会删除该流程定义下所有的任务、实例、记录
    repositoryService.deleteDeployment(deploymentId,true);
    System.out.println("删除流程定义成功");
}
```
## 启动


# 问题
> 配置文件中spring.database-schema-update(表不存在，自动创建)设置true时，启动报错，不能自动创建表

解决：在数据库连接url中添加参数`nullCatalogMeansCurrent=true`
> 当使用版本低于7.1.0.M6时，出现报错：`Unknown column 'VERSION_' in 'field list'`，这是Activiti7的官方BUG

1.在act_re_deployment中加两个字段，VERSION_和PROJECT_RELEASE_VERSION_然后重新运行
```java
-- ----------------------------
-- 修复Activiti7的M4版本缺失字段Bug
-- ----------------------------
alter table ACT_RE_DEPLOYMENT add column PROJECT_RELEASE_VERSION_ varchar(255) DEFAULT NULL;
alter table ACT_RE_DEPLOYMENT add column VERSION_ varchar(255) DEFAULT NULL;
```
2.修改版本  7.1.0.M6及以上

