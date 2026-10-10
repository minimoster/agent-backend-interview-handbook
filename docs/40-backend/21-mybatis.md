# MyBatis 参数与映射补充

[总目录](../../README.md) · [数据库补充](20-mysql-mechanisms.md)

<a id="fj36"></a>
### FJ36 Mapper、XML、注解与参数绑定是什么关系，如何防止 SQL 注入

**优先级：P0。**

**知识点详解**：MyBatis 的 Mapper 接口是调用入口，框架创建代理将方法映射到 SQL 语句；XML 与注解是定义映射语句的两种方式，并不和 Mapper 接口互斥。既可以通过 `session.getMapper(UserMapper.class)` 调用接口，也可以用 SqlSession 按语句全名调用，例如 selectOne("example.UserMapper.findById", id)。XML 的 namespace 通常对应接口全名，语句 id 对应方法；resultMap 负责更复杂的结果映射。

`#{value}` 让 MyBatis 为值参数生成 PreparedStatement 占位绑定；值作为数据传给数据库，不把引号、注释等输入当 SQL 结构拼接。`${value}` 是文本替换，会改变 SQL 文本，不能接收未经验证的用户输入。列名、表名、ASC/DESC 等标识符/关键字通常不能通过普通值占位来替代；用服务端固定允许列表选择完整片段，不是做几个字符串 replace 就认定安全。

动态 XML/注解并不使所有 SQL 自动安全。自己拼接字符串、滥用 `${}`、动态排序字段未经白名单，仍能引入注入风险。参数化也不等于授权，查询仍需从可信身份上下文限定 tenant_id；用户传合法的 id 也可能属于别人。

**具体例子**（未运行，简化 Mapper）：
```java
public interface UserMapper {
    @Select("SELECT id, name FROM app_user WHERE id = #{id}")
    User findById(@Param("id") long id);
}
```
它同时使用 Mapper 接口与注解。若排序输入为 `recent`，在服务端枚举映射成固定 `created_at DESC, id DESC`；其他输入拒绝，不将原始文本送进 `${orderBy}`。测试可包括输入单引号、注释、非法排序值与跨租户 id，但不能在真实生产库随意注入试验。

**面试答法**：Mapper 是调用方式，XML/注解是映射定义方式；值用 #{} 绑定，结构只能从可信允许列表选择，再独立做资源授权。

**追问**：`ORDER BY #{column}` 能动态选择列吗？值占位通常被视为值表达式，不能等同插入列标识符。一个方法参数多个值怎样绑定？可显式 @Param 命名并与映射保持一致。

**误区**：Mapper 与注解是二选一；MyBatis 自动消灭全部 SQL 注入；参数化会自动验证访问权限。

**一手来源**：[FJ-S103 MyBatis XML 与字符串替换](https://mybatis.org/mybatis-3/sqlmap-xml.html)、[FJ-S104 MyBatis Java API/Mapper](https://mybatis.org/mybatis-3/java-api.html)。以上代码未编译、未连接数据库。
