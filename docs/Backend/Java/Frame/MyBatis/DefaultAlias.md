# MyBatis 内置类型别名

对于普通的 Java 类型，有许多内建的类型别名。它们都是大小写不敏感的，由于重载的名字，要注意原生类型的特殊处理。

| 别名       | 映射的类型 |
| ---------- | ---------- |
| \_byte     | byte       |
| \_long     | long       |
| \_short    | short      |
| \_int      | int        |
| \_integer  | int        |
| \_double   | double     |
| \_float    | float      |
| \_boolean  | boolean    |
| string     | String     |
| byte       | Byte       |
| long       | Long       |
| short      | Short      |
| int        | Integer    |
| integer    | Integer    |
| double     | Double     |
| float      | Float      |
| boolean    | Boolean    |
| date       | Date       |
| decimal    | BigDecimal |
| bigdecimal | BigDecimal |
| object     | Object     |
| map        | Map        |
| hashmap    | HashMap    |
| list       | List       |
| arraylist  | ArrayList  |
| collection | Collection |
| iterator   | Iterator   |

:::danger 注意

不光可以写java.lang.Integer 也可以写Integer、integer、int、Int、\_int

:::
