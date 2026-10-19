# Loon 去开屏广告与去广告规则 · 自动同步

> 将 [hwind2021/QuantumultX-AdBlock-CN](https://github.com/hwind2021/QuantumultX-AdBlock-CN) 的三套 **Quantumult X（QX）广告过滤规则**，每 **12 小时**自动同步、校验并转换为 **Loon 原生远程规则**。本仓库是**第三方兼容转换项目**，不是原作者的官方 Loon 发行版，也不是自行研发的新广告库。

**适用：Loon（iPhone / iPad）**　｜　**规则类型：远程规则（Remote Rule）**　｜　**策略：`REJECT`**　｜　**无需 MITM**。

## 一、三套规则分别有什么用？

| 规则 | 主要用途（沿用上游说明） | 初始规则数¹ | 适用场景 |
| --- | --- | ---: | --- |
| **Splash-Killer** | **开屏广告专项**：拦截穿山甲、广点通、百青藤、快手、阿里妈妈、AdMob、AppLovin 等常见广告 SDK 的相关域名 | 473 | 更重视启动开屏广告拦截 |
| **BlockHttpDNS** | **阻断 HTTPDNS**：限制 APP 使用独立的 HTTPDNS 服务绕过系统 DNS 的拦截路径 | 62 | 当 APP 绕过常规广告域名拦截时辅助使用 |
| **AdBlock-Lite** | **综合广告拦截**：作者整合开屏规则、经多个来源交叉筛选的广告域名及 HTTPDNS 相关规则，兼顾体量与覆盖 | 22,739 | 推荐优先单独测试的综合版 |

¹ 规则数为 **2026-10-19** 首次生成时的数量，并非固定数量；最新数量及**上游更新时间**请查看对应文件顶部。

**注意：** 它们是**域名/IP 分流规则**，并不是针对每一个 APP 精修界面的 Rewrite 脚本；不保证新版 APP 的所有开屏广告都能去掉。HTTPDNS 拦截可能影响部分 APP 的解析、加载或功能，请自行测试。

## 二、直接订阅（Loon）

| 订阅 | 点击查看原生 Loon 规则 |
| --- | --- |
| **Splash-Killer · 开屏广告** | [Splash-Killer.list](https://raw.githubusercontent.com/sndjdndi/Loon-AdBlock-Sync/main/loon/Splash-Killer.list) |
| **BlockHttpDNS · HTTPDNS 拦截** | [BlockHttpDNS.list](https://raw.githubusercontent.com/sndjdndi/Loon-AdBlock-Sync/main/loon/BlockHttpDNS.list) |
| **AdBlock-Lite · 综合去广告** | [AdBlock-Lite.list](https://raw.githubusercontent.com/sndjdndi/Loon-AdBlock-Sync/main/loon/AdBlock-Lite.list) |

**添加步骤：**

1. 打开 **Loon → 规则 → 远程规则（Remote Rule）**。
2. 新增远程规则，将上方对应的 Raw 地址粘贴进去。
3. **策略选择 `REJECT`（拒绝），不是 `DIRECT`。**
4. 开启订阅并更新，让 Loon 加载规则；之后可按照 Loon 的远程规则更新机制刷新。
5. **建议先只启用 AdBlock-Lite 一套**。因为它与另外两套、秋风 AWAvenue、Cats-Team AdRules、217heidai Loon Lite 都可能重叠。需要排查时不要全部同时打开。

> **不要把以上三个 `.list` 添加到 Loon 的「插件」页面。** 它们是远程规则，**无需 MITM 证书**。已单独安装的墨鱼去开屏 Rewrite 插件属于另一类功能，可分别测试是否需要保留。

## 三、这个项目怎么来的？是不是搬运？

- **原始作者与维护者：** [hwind2021 / QuantumultX-AdBlock-CN](https://github.com/hwind2021/QuantumultX-AdBlock-CN)。本仓库并不声称原创上游规则。
- **上游格式：** Quantumult X 的 `quantumultx/filter/` 下三个 `.list`，例如 `HOST-SUFFIX,example.com,REJECT`。
- **自动转换：** 通过本仓库的 [sync.py](sync.py) 将 `HOST` 转为 `DOMAIN`、`HOST-SUFFIX` 转为 `DOMAIN-SUFFIX`、`HOST-KEYWORD` 转为 `DOMAIN-KEYWORD`、`IP6-CIDR` 转为 `IP-CIDR6`；`IP-CIDR` 继续使用原名。输出文件不写死策略，统一在 Loon 订阅时选择 `REJECT`。
- **内容继承：** 转换不增加广告域名、也不自行判断广告规则是否有效，只处理兼容语法、去重与安全校验；保留**原 QX 文件中作者标注的 UPDATED 时间**、规则说明与来源。
- **版权与出处：** 参见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 和 [上游 LICENSE](https://github.com/hwind2021/QuantumultX-AdBlock-CN/blob/main/LICENSE)。上游注明其规则数据还涉及 blackmatrix7 与 anti-AD 等项目。

### 格式对照示例

```text
# 原始 QX：HOST-SUFFIX,example.com,REJECT
# 转换 Loon：DOMAIN-SUFFIX,example.com
# 在 Loon 添加远程规则时：策略选择 REJECT
```

## 四、自动更新及更新时间说明

- **检查周期：每 12 小时一次。** GitHub Actions 使用 UTC 时间 `17 */12 * * *`，约在 **北京时间 08:17 / 20:17** 检查上游。GitHub 定时运行可能延迟，不保证精确到分钟。
- **手动更新：** 进入仓库 [Actions → Sync QX AdBlock to Loon](https://github.com/sndjdndi/Loon-AdBlock-Sync/actions/workflows/update.yml)，点击 **Run workflow**。
- **生成规则头：** 显示 `#!date`、`上游更新时间`、`自动检查间隔` 等说明。**这里的日期来自上游原始文件的 `# UPDATED`，不是你打开页面的时间，也不一定是 Actions 的实际执行时间。**
- **只有内容变化才提交：** 对照上游的实际规则及文件头，若没有变化，GitHub 不会反复提交。
- **失败保护：** 下载失败、上游结构或规则语法发生未知变化、规则数量异常时中止，不提交损坏的规则文件。具体构建记录可在 Actions 查看。
- **注意**：公开仓库长时间无活动可能导致 GitHub 自动停止计划任务，届时需在 Actions 中重新启用。

## 五、自己运行与测试

需 Python 3.10+，使用标准库，无额外依赖。

```bash
python3 -m unittest discover -s tests -v
python3 sync.py --dry-run
python3 sync.py
```

**免责声明：** 本仓库与 hwind2021 原作者没有从属或官方合作关系，不保证规则的时效性和对所有 APP 的适配。遇到 APP 无法联网、登录异常、页面缺失等问题，先关闭可疑规则测试，尤其是 HTTPDNS 拦截。

— 规则版权归其各自作者，本项目仅提供 QX → Loon 的自动格式转换和订阅托管。
