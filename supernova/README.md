# 超新星检测

## 运行方式

### 进入python运行环境

下面命令需要在最开始执行，否则会显示缺少python包

`
. activate skysurvey
`

### 更新数据库


下面的命令将更新DATE日期指定的超星新数据库supernovae。（约30min）

`
python ./supernova.py update --date <DATE>
`

### 查询数据库完整性

如果需要查询哪些日期的超新星数据尚且没有被完全写入数据库，运行下面的命令，该命令将比较数据库中的每一天的数据条数。（约1min）

`
python ./supernova.py info
`
