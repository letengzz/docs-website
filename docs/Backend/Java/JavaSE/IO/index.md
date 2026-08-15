# IO 流

Java IO 流是用于处理输入输出操作的核心 API，提供了对文件、网络连接、内存等数据源的读写能力。Java IO 分为字节流和字符流两大类。

## IO 流概述

### 分类体系

```text
IO 流
├── 字节流（以字节为单位处理）
│   ├── InputStream（输入字节流）
│   │   ├── FileInputStream
│   │   ├── BufferedInputStream
│   │   ├── ObjectInputStream
│   │   └── ByteArrayInputStream
│   └── OutputStream（输出字节流）
│       ├── FileOutputStream
│       ├── BufferedOutputStream
│       ├── ObjectOutputStream
│       └── ByteArrayOutputStream
│
└── 字符流（以字符为单位处理）
    ├── Reader（输入字符流）
    │   ├── InputStreamReader
    │   ├── FileReader
    │   ├── BufferedReader
    │   └── StringReader
    └── Writer（输出字符流）
        ├── OutputStreamWriter
        ├── FileWriter
        ├── BufferedWriter
        └── StringWriter
```

## 字节流

### FileInputStream 与 FileOutputStream

```java
// IO/FileStreamDemo.java
import java.io.*;

public class FileStreamDemo {
    public static void main(String[] args) {
        String sourceFile = "source.txt";
        String destFile = "dest.txt";
        
        // 创建测试文件
        try (OutputStream os = new FileOutputStream(sourceFile)) {
            os.write("Hello, Java IO!\n这是中文内容".getBytes());
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // 使用 FileInputStream 读取文件
        System.out.println("=== 使用字节流读取文件 ===");
        try (InputStream is = new FileInputStream(sourceFile)) {
            int data;
            // 逐字节读取
            while ((data = is.read()) != -1) {
                System.out.print((char) data);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // 使用字节数组读取（推荐）
        System.out.println("\n=== 使用字节数组读取 ===");
        try (InputStream is = new FileInputStream(sourceFile)) {
            byte[] buffer = new byte[1024];
            int bytesRead;
            StringBuilder content = new StringBuilder();
            while ((bytesRead = is.read(buffer)) != -1) {
                content.append(new String(buffer, 0, bytesRead));
            }
            System.out.println(content);
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // 使用 FileOutputStream 写入文件
        System.out.println("\n=== 使用字节流写入文件 ===");
        try (OutputStream os = new FileOutputStream(destFile)) {
            String content = "这是写入的内容\n第二行内容";
            os.write(content.getBytes());
            os.flush();  // 确保数据写入
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // 文件复制
        System.out.println("\n=== 文件复制 ===");
        copyFile(sourceFile, destFile + "_copy.txt");
        System.out.println("文件复制完成");
    }
    
    public static void copyFile(String source, String dest) {
        try (InputStream is = new FileInputStream(source);
             OutputStream os = new FileOutputStream(dest)) {
            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = is.read(buffer)) != -1) {
                os.write(buffer, 0, bytesRead);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### BufferedInputStream 与 BufferedOutputStream

```java
// IO/BufferedStreamDemo.java
import java.io.*;

public class BufferedStreamDemo {
    public static void main(String[] args) {
        String sourceFile = "large_source.dat";
        String destFile = "large_dest.dat";
        
        // 创建大文件用于测试
        createLargeFile(sourceFile, 1024 * 1024 * 10);  // 10MB
        
        // 不使用缓冲流
        long startTime = System.currentTimeMillis();
        copyFileWithBuffer(sourceFile, "temp1.dat", false);
        long noBufferTime = System.currentTimeMillis() - startTime;
        
        // 使用缓冲流
        startTime = System.currentTimeMillis();
        copyFileWithBuffer(sourceFile, "temp2.dat", true);
        long bufferTime = System.currentTimeMillis() - startTime;
        
        System.out.println("不使用缓冲流耗时: " + noBufferTime + "ms");
        System.out.println("使用缓冲流耗时: " + bufferTime + "ms");
        
        // 清理临时文件
        new File("temp1.dat").delete();
        new File("temp2.dat").delete();
    }
    
    public static void createLargeFile(String filename, int size) {
        try (OutputStream os = new FileOutputStream(filename)) {
            byte[] data = new byte[1024];
            int written = 0;
            while (written < size) {
                int toWrite = Math.min(data.length, size - written);
                os.write(data, 0, toWrite);
                written += toWrite;
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    public static void copyFileWithBuffer(String source, String dest, boolean useBuffer) {
        try (InputStream is = new FileInputStream(source);
             OutputStream os = new FileOutputStream(dest)) {
            
            if (useBuffer) {
                // 使用缓冲流
                try (BufferedInputStream bis = new BufferedInputStream(is);
                     BufferedOutputStream bos = new BufferedOutputStream(os)) {
                    byte[] buffer = new byte[8192];
                    int bytesRead;
                    while ((bytesRead = bis.read(buffer)) != -1) {
                        bos.write(buffer, 0, bytesRead);
                    }
                }
            } else {
                // 不使用缓冲流
                byte[] buffer = new byte[8192];
                int bytesRead;
                while ((bytesRead = is.read(buffer)) != -1) {
                    os.write(buffer, 0, bytesRead);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### ObjectInputStream 与 ObjectOutputStream

```java
// IO/ObjectStreamDemo.java
import java.io.*;

public class ObjectStreamDemo {
    public static void main(String[] args) {
        String objectFile = "objects.dat";
        
        // 序列化对象
        System.out.println("=== 对象序列化 ===");
        try (ObjectOutputStream oos = new ObjectOutputStream(
                new FileOutputStream(objectFile))) {
            
            User user = new User("张三", 25, "zhangsan@example.com");
            oos.writeObject(user);
            
            java.util.ArrayList<String> list = new java.util.ArrayList<>();
            list.add("item1");
            list.add("item2");
            oos.writeObject(list);
            
            System.out.println("对象序列化完成");
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // 反序列化对象
        System.out.println("\n=== 对象反序列化 ===");
        try (ObjectInputStream ois = new ObjectInputStream(
                new FileInputStream(objectFile))) {
            
            User user = (User) ois.readObject();
            System.out.println("用户信息: " + user);
            
            @SuppressWarnings("unchecked")
            java.util.ArrayList<String> list = (java.util.ArrayList<String>) ois.readObject();
            System.out.println("列表内容: " + list);
            
        } catch (IOException | ClassNotFoundException e) {
            e.printStackTrace();
        }
    }
}

class User implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private String name;
    private transient int age;  // transient 修饰的字段不参与序列化
    private String email;
    
    public User(String name, int age, String email) {
        this.name = name;
        this.age = age;
        this.email = email;
    }
    
    @Override
    public String toString() {
        return "User{name='" + name + "', age=" + age + ", email='" + email + "'}";
    }
}
```

## 字符流

### InputStreamReader 与 OutputStreamWriter

```java
// IO/CharacterStreamDemo.java
import java.io.*;

public class CharacterStreamDemo {
    public static void main(String[] args) {
        String file = "character_test.txt";
        
        // 使用 OutputStreamWriter 写入（可指定编码）
        System.out.println("=== 使用字符流写入 ===");
        try (OutputStreamWriter osw = new OutputStreamWriter(
                new FileOutputStream(file), "UTF-8")) {
            osw.write("Hello, 字符流!\n");
            osw.write("这是第二行\n");
            osw.write("支持中文写入");
            osw.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // 使用 InputStreamReader 读取（可指定编码）
        System.out.println("\n=== 使用字符流读取 ===");
        try (InputStreamReader isr = new InputStreamReader(
                new FileInputStream(file), "UTF-8")) {
            int data;
            while ((data = isr.read()) != -1) {
                System.out.print((char) data);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // 使用字符数组读取
        System.out.println("\n=== 使用字符数组读取 ===");
        try (InputStreamReader isr = new InputStreamReader(
                new FileInputStream(file), "UTF-8")) {
            char[] buffer = new char[1024];
            int charsRead;
            StringBuilder content = new StringBuilder();
            while ((charsRead = isr.read(buffer)) != -1) {
                content.append(buffer, 0, charsRead);
            }
            System.out.println(content);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### FileReader 与 FileWriter

```java
// IO/FileReaderWriterDemo.java
import java.io.*;

public class FileReaderWriterDemo {
    public static void main(String[] args) {
        String sourceFile = "source.txt";
        String destFile = "dest.txt";
        
        // 使用 FileWriter 写入
        System.out.println("=== 使用 FileWriter 写入 ===");
        try (FileWriter fw = new FileWriter(destFile)) {
            fw.write("这是第一行内容\n");
            fw.write("这是第二行内容\n");
            fw.append("这是追加的内容");
            fw.flush();
            System.out.println("写入完成");
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // 使用 FileReader 读取
        System.out.println("\n=== 使用 FileReader 读取 ===");
        try (FileReader fr = new FileReader(destFile)) {
            int data;
            while ((data = fr.read()) != -1) {
                System.out.print((char) data);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // 文件复制
        System.out.println("\n=== 文件复制（字符流） ===");
        copyFileWithCharStream(sourceFile, "char_copy.txt");
    }
    
    public static void copyFileWithCharStream(String source, String dest) {
        try (FileReader fr = new FileReader(source);
             FileWriter fw = new FileWriter(dest)) {
            char[] buffer = new char[8192];
            int charsRead;
            while ((charsRead = fr.read(buffer)) != -1) {
                fw.write(buffer, 0, charsRead);
            }
            fw.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### BufferedReader 与 BufferedWriter

```java
// IO/BufferedReaderWriterDemo.java
import java.io.*;

public class BufferedReaderWriterDemo {
    public static void main(String[] args) {
        String file = "buffered_test.txt";
        
        // 使用 BufferedWriter 写入
        System.out.println("=== 使用 BufferedWriter 写入 ===");
        try (BufferedWriter bw = new BufferedWriter(
                new FileWriter(file))) {
            bw.write("这是第一行");
            bw.newLine();  // 写入换行符
            bw.write("这是第二行");
            bw.newLine();
            bw.write("这是第三行");
            bw.flush();
            System.out.println("写入完成");
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // 使用 BufferedReader 读取
        System.out.println("\n=== 使用 BufferedReader 读取 ===");
        try (BufferedReader br = new BufferedReader(
                new FileReader(file))) {
            String line;
            while ((line = br.readLine()) != null) {
                System.out.println(line);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // 读取大文件并统计行数
        System.out.println("\n=== 统计文件行数 ===");
        try (BufferedReader br = new BufferedReader(new FileReader(file))) {
            long lineCount = br.lines().count();
            System.out.println("文件总行数: " + lineCount);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

## 缓冲流与高效 IO

```java
// IO/HighPerformanceDemo.java
import java.io.*;

public class HighPerformanceDemo {
    public static void main(String[] args) {
        // 最佳实践：使用缓冲流包装
        System.out.println("=== 高效 IO 最佳实践 ===");
        
        String source = "performance_source.dat";
        String dest = "performance_dest.dat";
        
        // 创建测试数据
        createTestData(source, 1024 * 1024);  // 1MB
        
        long startTime = System.currentTimeMillis();
        
        // 推荐方式：缓冲流 + 适当缓冲区大小
        try (InputStream is = new BufferedInputStream(
                new FileInputStream(source), 64 * 1024);
             OutputStream os = new BufferedOutputStream(
                new FileOutputStream(dest), 64 * 1024)) {
            
            byte[] buffer = new byte[64 * 1024];  // 64KB 缓冲区
            int bytesRead;
            while ((bytesRead = is.read(buffer)) != -1) {
                os.write(buffer, 0, bytesRead);
            }
            os.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        long elapsedTime = System.currentTimeMillis() - startTime;
        System.out.println("复制耗时: " + elapsedTime + "ms");
        
        // 清理
        new File(source).delete();
        new File(dest).delete();
    }
    
    public static void createTestData(String filename, int size) {
        try (OutputStream os = new FileOutputStream(filename)) {
            byte[] data = new byte[1024];
            for (int i = 0; i < size / data.length; i++) {
                os.write(data);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

## NIO（New IO）

### Path 与 Files

```java
// IO/NioDemo.java
import java.io.IOException;
import java.nio.file.*;

public class NioDemo {
    public static void main(String[] args) {
        Path dir = Paths.get("nio_test");
        Path file = dir.resolve("test.txt");
        Path link = dir.resolve("link.txt");
        
        try {
            // 创建目录
            if (!Files.exists(dir)) {
                Files.createDirectory(dir);
                System.out.println("目录创建成功: " + dir);
            }
            
            // 写入文件
            Files.writeString(file, "这是 NIO 写入的内容\n第二行", StandardOpenOption.CREATE);
            System.out.println("文件写入成功");
            
            // 读取文件
            String content = Files.readString(file);
            System.out.println("文件内容:\n" + content);
            
            // 复制文件
            Path copy = dir.resolve("copy.txt");
            Files.copy(file, copy, StandardCopyOption.REPLACE_EXISTING);
            System.out.println("文件复制成功");
            
            // 移动/重命名文件
            Path moved = dir.resolve("moved.txt");
            Files.move(copy, moved, StandardCopyOption.REPLACE_EXISTING);
            System.out.println("文件移动成功");
            
            // 创建符号链接
            if (!Files.exists(link)) {
                Files.createSymbolicLink(link, file);
                System.out.println("符号链接创建成功");
            }
            
            // 遍历目录
            System.out.println("\n目录内容:");
            try (DirectoryStream<Path> stream = Files.newDirectoryStream(dir)) {
                for (Path entry : stream) {
                    System.out.println("  " + entry.getFileName() + 
                        (Files.isDirectory(entry) ? " (目录)" : " (文件)"));
                }
            }
            
            // 遍历目录树
            System.out.println("\n目录树:");
            Files.walk(dir).forEach(p -> System.out.println("  " + p));
            
            // 文件属性
            System.out.println("\n文件属性:");
            System.out.println("是否存在: " + Files.exists(file));
            System.out.println("是否为目录: " + Files.isDirectory(file));
            System.out.println("是否为文件: " + Files.isRegularFile(file));
            System.out.println("文件大小: " + Files.size(file) + " 字节");
            System.out.println("可读: " + Files.isReadable(file));
            System.out.println("可写: " + Files.isWritable(file));
            
            // 删除
            Files.deleteIfExists(link);
            deleteDirectory(dir);
            
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    public static void deleteDirectory(Path dir) throws IOException {
        Files.walk(dir)
             .sorted((a, b) -> b.compareTo(a))  // 先删除子文件
             .forEach(p -> {
                 try {
                     Files.delete(p);
                 } catch (IOException e) {
                     e.printStackTrace();
                 }
             });
    }
}
```

### 通道与缓冲区

```java
// IO/ChannelBufferDemo.java
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;

public class ChannelBufferDemo {
    public static void main(String[] args) {
        String sourceFile = "channel_source.dat";
        String destFile = "channel_dest.dat";
        
        try {
            // 创建测试文件
            createTestFile(sourceFile, 1024 * 1024);
            
            // 使用 NIO 通道复制文件（直接缓冲区）
            System.out.println("=== 使用 NIO 通道复制 ===");
            long startTime = System.currentTimeMillis();
            
            try (FileChannel sourceChannel = FileChannel.open(
                    Paths.get(sourceFile), StandardOpenOption.READ);
                 FileChannel destChannel = FileChannel.open(
                    Paths.get(destFile), 
                    StandardOpenOption.CREATE, 
                    StandardOpenOption.WRITE,
                    StandardOpenOption.TRUNCATE_EXISTING)) {
                
                long size = sourceChannel.size();
                sourceChannel.transferTo(0, size, destChannel);
            }
            
            long elapsedTime = System.currentTimeMillis() - startTime;
            System.out.println("NIO 复制耗时: " + elapsedTime + "ms");
            
            // 使用缓冲区读写
            System.out.println("\n=== 使用缓冲区读写 ===");
            try (FileChannel channel = FileChannel.open(
                    Paths.get(destFile), StandardOpenOption.READ, StandardOpenOption.WRITE)) {
                
                ByteBuffer buffer = ByteBuffer.allocate(1024);
                
                // 写入数据
                buffer.put("Hello, NIO Buffer!".getBytes());
                buffer.flip();  // 切换为读模式
                channel.write(buffer);
                channel.force(true);
                
                // 读取数据
                buffer.clear();
                channel.position(0);
                channel.read(buffer);
                buffer.flip();
                byte[] bytes = new byte[buffer.remaining()];
                buffer.get(bytes);
                System.out.println("读取内容: " + new String(bytes));
                
                // 使用内存映射文件
                System.out.println("\n=== 内存映射文件 ===");
                try (FileChannel mapChannel = FileChannel.open(
                        Paths.get("mmap_test.dat"), 
                        StandardOpenOption.CREATE, 
                        StandardOpenOption.READ, 
                        StandardOpenOption.WRITE)) {
                    
                    long fileSize = 1024 * 1024;  // 1MB
                    mapChannel.truncate(fileSize);
                    
                    MappedByteBuffer mbb = mapChannel.map(
                        FileChannel.MapMode.READ_WRITE, 0, fileSize);
                    
                    // 写入
                    for (int i = 0; i < 100; i++) {
                        mbb.putInt(i * 4, i);
                    }
                    
                    // 读取
                    System.out.println("读取第 50 个整数: " + mbb.getInt(50 * 4));
                }
            }
            
            // 清理
            new File(sourceFile).delete();
            new File(destFile).delete();
            new File("mmap_test.dat").delete();
            
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    public static void createTestFile(String filename, int size) throws IOException {
        try (FileChannel channel = FileChannel.open(
                Paths.get(filename), 
                StandardOpenOption.CREATE, 
                StandardOpenOption.WRITE)) {
            
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            byte[] data = new byte[1024];
            long written = 0;
            
            while (written < size) {
                buffer.put(data);
                buffer.flip();
                channel.write(buffer);
                buffer.clear();
                written += 1024;
            }
        }
    }
}
```

::: tip IO 选择指南
| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| 文本文件读写 | BufferedReader/Writer | 高效，支持按行读写 |
| 二进制文件读写 | BufferedInputStream/OutputStream | 字节流，效率高 |
| 对象序列化 | ObjectInputStream/OutputStream | 简单易用 |
| 大文件处理 | NIO + 内存映射 | 性能最优 |
| 文件复制 | Files.copy 或 transferTo | 简洁高效 |
| 配置读取 | Properties 或 NIO | 简单便捷 |
:::
