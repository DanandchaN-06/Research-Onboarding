# scikit-learn 速查笔记

> 🧭 本页是 **scikit-learn 的工程速查**，面向「实际写代码时随手查」。不追求覆盖全库，只收录最常用的接口与最容易翻车的坑。

> ⚙️ **读前约定**：约定 `X` 是特征矩阵（二维）、`y` 是标签；`#` 后为说明；所有 `random_state` 都建议显式指定。

## 一、scikit-learn 是什么

### 1.1 一句话定义

scikit-learn（简称 sklearn）是 Python 最主流的**传统机器学习库**。它把「数据划分 → 预处理 → 训练模型 → 预测 → 评估」这一整套流程做成了统一的接口，让你用几行代码就能跑通一个完整实验。
它管的是**经典机器学习**（线性模型、树模型、聚类、降维等），**不包含深度学习**。神经网络要用 PyTorch / TensorFlow，sklearn 只负责它们前面那段数据准备。

### 1.2 它和 NumPy 是什么关系

sklearn 建在 NumPy 和 SciPy 之上，所以**输入输出的数据格式就是 NumPy 数组**：

- 特征矩阵习惯记作 `X`，形状 `(n_samples, n_features)`，**二维**。
- 标签记作 `y`，回归任务形状 `(n_samples,)`，分类任务也是 `(n_samples,)`。
- 昨天学的 `shape` 检查、索引切片、`np.dot` 在这里全部继续生效。

### 1.3 为什么它值得单独记一份速查表

sklearn 的 API 有个非常大的好处：**所有模型长得几乎一样**。只要记住三个方法，就能用遍全库：
下表回答的是：一个 sklearn 模型对象身上最核心的三个方法分别干什么。

| **方法** | **作用** | **注意** |
| --- | --- | --- |
| `model.fit(X, y)` | 用数据训练模型 | 无监督算法只传 `X` |
| `model.predict(X)` | 用训练好的模型做预测 | 返回预测值 |
| `model.score(X, y)` | 直接给出评估分数 | 回归是 $`R^2`$，分类是准确率 |

> 💡 **这一页要记住的核心**：sklearn 的一切都是 `fit` / `predict` / `transform` 三个动作的组合。看到任何新模型，先猜它怎么 fit、怎么 predict，基本不会错。

## 二、第一步：划分数据集

### 2.1 为什么要划分

模型在**训练过的数据上表现好**不代表它真的学到了规律——它可能只是把答案背下来了。所以要留一部分数据完全不参与训练，专门用来检验。

- **训练集**：用来 `fit`，模型从这里学。
- **测试集**：只在最后用一次，检验泛化能力。
- 两者**绝不能混用**，否则评估结果会虚高。

### 2.2 train_test_split

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,      # 测试集占比 20%
    random_state=42,    # 固定随机种子，保证可复现
    stratify=y          # 分类任务按类别比例分层抽样
)
```

下表回答的是：`train_test_split` 的常用参数各自影响什么。

| **参数** | **含义** |
| --- | --- |
| `test_size` | 测试集比例（0.2 表示 20%）或样本个数 |
| `random_state` | 随机种子，**不填每次划分结果都不同** |
| `stratify=y` | 分类任务按标签比例分层，避免某类全被分走 |
| `shuffle` | 是否打乱，默认 True |

> ⚠️ **参数顺序是坑**：返回值顺序固定是 `X_train, X_test, y_train, y_test`——**先 X 后 y、每组内部先 train 后 test**。写反了不会报错，但模型会评出一堆垃圾分数。

## 三、数据预处理

### 3.1 为什么必须预处理

原始数据常常量纲不一（一个特征是 0.001 量级，另一个是 10000 量级），或者有缺失值、文字标签。很多算法对这类问题很敏感，必须先把数据「洗」成统一规格。

### 3.2 标准化与归一化

这两个词最容易混。它们的区别在于**把数据压到什么范围**：
下表回答的是：标准化和归一化的公式与适用场景差异。

| **方法** | **做了什么** | **结果范围** | **什么时候用** |
| --- | --- | --- | --- |
| `StandardScaler` | 减均值、除标准差 | 均值 0、方差 1 | **默认首选**，对离群值更稳 |
| `MinMaxScaler` | 线性拉伸到区间 | $`[0, 1]`$ | 需要固定范围时（如图像像素） |
| `RobustScaler` | 用中位数和四分位距 | — | 数据里离群值很多时 |

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # 训练集：fit + transform
X_test_scaled  = scaler.transform(X_test)        # 测试集：只用 transform
```

> ⚠️ **这是新手最容易犯的错**：测试集只能 transform，**绝对不能 fit**。如果用测试集自己的均值方差去标准化，等于提前偷看了测试数据（数据泄漏）。

> 💡 规律记法：**训练集用 fit_transform，测试集用 transform**。同一个 Scaler 对象贯穿两处，参数来自训练集。

### 3.3 编码类别特征

文字不能直接进模型，要先变成数字。

| **编码器** | **适用** | **说明** |
| --- | --- | --- |
| `LabelEncoder` | 标签 `y` | 把类别映射成 0,1,2… |
| `OrdinalEncoder` | 有序特征 | 有大小关系的类别（低/中/高） |
| `OneHotEncoder` | 无序特征 | 每个类别一列 0/1，避免虚假大小关系 |

> ⚠️ **别用 LabelEncoder 处理无序特征**。它会给「北京=0、上海=1、广州=2」这种毫无意义的顺序，模型会误以为广州比北京「大」。无序特征一律用 `OneHotEncoder`。

### 3.4 处理缺失值与 Pipeline

```python
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="mean")),   # 缺失值填均值
    ("scaler", StandardScaler()),
    ("model", SomeModel())
])
pipe.fit(X_train, y_train)     # 一次 fit 跑完全流程
```

`Pipeline` 的价值：把预处理和模型打包成一个整体，**交叉验证时不会泄漏**，因为每一折的预处理都只在训练部分 fit。

> 💡 **只要流程超过两步，就上 Pipeline**。它除了防止数据泄漏，还省掉了手工管理多个中间变量的麻烦，调参时也只需要改 `model__参数名`。

## 四、常用模型

### 4.1 怎么选模型

先看任务类型，再看数据规模与是否需要解释性：

- **预测连续值** → 回归模型
- **预测类别** → 分类模型
- **没有标签、想找结构** → 聚类 / 降维

### 4.2 线性模型

下表回答的是：四类线性模型各自适合什么任务。

| **模型** | **任务** | **一句话** |
| --- | --- | --- |
| `LinearRegression` | 回归 | 最小二乘，最基础的线性回归 |
| `Ridge` | 回归 | L2 正则，压制系数防止过拟合 |
| `Lasso` | 回归 | L1 正则，能把不重要的系数压成 0（自带特征选择） |
| `LogisticRegression` | 分类 | 名字叫回归，**其实做分类**，输出概率 |

```python
from sklearn.linear_model import LogisticRegression

clf = LogisticRegression(max_iter=1000)   # 迭代次数调大，避免不收敛警告
clf.fit(X_train, y_train)
print(clf.predict_proba(X_test)[:, 1])    # 输出属于正类的概率
```

### 4.3 树模型与集成

| **模型** | **特点** |
| --- | --- |
| `DecisionTreeClassifier` / `Regressor` | 单棵树，好解释，**极易过拟合** |
| `RandomForestClassifier` | 多棵树投票，抗过拟合，**表格数据的强基线** |
| `GradientBoostingClassifier` | 逐步纠错，精度高，训练慢 |
| `HistGradientBoostingClassifier` | 大数据集上的加速版，**推荐优先试** |

> 💡 **实战经验**：拿到一份表格数据不知道用什么，先跑 `RandomForest` 或 `HistGradientBoosting`，几乎总能拿到不错的结果，再拿它当基线去比较其他模型。

### 4.4 无监督：聚类与降维

| **模型** | **用途** |
| --- | --- |
| `KMeans` | 把样本分成 K 簇，需**提前指定 K** |
| `DBSCAN` | 按密度聚类，能自动识别噪声点 |
| `PCA` | 降维，把高维数据压到少数几个主成分上 |

```python
from sklearn.cluster import KMeans
km = KMeans(n_clusters=3, random_state=42)
km.fit_predict(X)          # 无监督：只传 X，没有 y
print(km.labels_)          # 每个样本的簇编号
```

> ⚠️ 无监督模型**没有 y**，所以 `fit(X)` 只传一个参数，评估也用 `score` 之外的方法（如轮廓系数）。别习惯性地塞两个参数进去。

## 五、模型评估

### 5.1 回归指标

| **指标** | **含义** |
| --- | --- |
| `mean_squared_error` | 均方误差，越小越好 |
| `mean_absolute_error` | 平均绝对误差，和原数据同量纲，**更好解释** |
| `r2_score` | $`R^2`$，越接近 1 越好，0 表示等于只预测均值 |

### 5.2 分类指标

| **指标** | **含义** |
| --- | --- |
| `accuracy_score` | 准确率，**类别不平衡时会骗人** |
| `precision_score` | 精确率：预测为正的里面，真正为正的比例 |
| `recall_score` | 召回率：真正为正的里面，被找出来的比例 |
| `f1_score` | 精确率与召回率的调和平均 |
| `confusion_matrix` | 混淆矩阵，看清每一类错在哪 |

```python
from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred))   # 一次输出 precision/recall/f1
```

> ⚠️ **准确率陷阱**：如果 99% 的样本都是负类，模型无脑全猜负类也能拿 99% 准确率。这种时候必须看精确率、召回率或 F1。类别不平衡优先看 **F1 或 AUC**。

## 六、交叉验证与调参

### 6.1 交叉验证

只划分一次训练/测试集，结果会受「运气」影响。交叉验证把数据切成 K 份，轮流留一份做验证，结果更可靠。

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(model, X, y, cv=5)   # 5 折交叉验证
print(scores.mean())                          # 平均分，比单次划分可信
```

### 6.2 网格搜索调参

```python
from sklearn.model_selection import GridSearchCV

param_grid = {"C": [0.01, 0.1, 1, 10], "penalty": ["l2"]}
grid = GridSearchCV(LogisticRegression(max_iter=1000), param_grid, cv=5)
grid.fit(X_train, y_train)

print(grid.best_params_)    # 最佳参数
print(grid.best_estimator_) # 最佳模型对象
```

| **工具** | **说明** |
| --- | --- |
| `GridSearchCV` | 穷举所有参数组合，**慢但彻底** |
| `RandomizedSearchCV` | 随机采样指定次数，参数多时更快 |

> ⚠️ 调参必须**只用训练集**，最后才用测试集验证一次。如果拿测试集去挑参数，测试集就变成了「训练数据」，评估结果不再可信。

## 七、速查表

### 7.1 全流程骨架

下表回答的是：一个完整实验从头到尾要按什么顺序调用什么。

| **步骤** | **代码** |
| --- | --- |
| 1 划分 | `train_test_split(X, y, test_size=0.2, random_state=42)` |
| 2 预处理 | `scaler.fit_transform(X_train)`  然后 `scaler.transform(X_test)` |
| 3 建模 | `model.fit(X_train, y_train)` |
| 4 预测 | `y_pred = model.predict(X_test)` |
| 5 评估 | `classification_report(y_test, y_pred)` 或 `r2_score` |
| 6 调参 | `GridSearchCV(model, param_grid, cv=5).fit(X_train, y_train)` |

### 7.2 常用模块导入路径

下表回答的是：常用类分别要从哪个子模块 import。

| **名字** | **导入路径** |
| --- | --- |
| `train_test_split`, `GridSearchCV`, `cross_val_score` | `sklearn.model_selection` |
| `StandardScaler`, `MinMaxScaler`, `OneHotEncoder` | `sklearn.preprocessing` |
| `SimpleImputer` | `sklearn.impute` |
| `Pipeline` | `sklearn.pipeline` |
| `LinearRegression`, `Ridge`, `Lasso`, `LogisticRegression` | `sklearn.linear_model` |
| `RandomForestClassifier`, `DecisionTreeRegressor` | `sklearn.ensemble` / `sklearn.tree` |
| `KMeans`, `DBSCAN` | `sklearn.cluster` |
| `PCA` | `sklearn.decomposition` |
| `accuracy_score`, `f1_score`, `r2_score` | `sklearn.metrics` |

### 7.3 易错点对照

下表回答的是：新手高频踩的坑对应怎么修。

| **坑** | **正确做法** |
| --- | --- |
| 测试集做了 `fit` | 训练集 `fit_transform`，测试集只 `transform` |
| 用 `LabelEncoder` 编无序特征 | 改用 `OneHotEncoder` |
| 划分返回值顺序记错 | 固定是 `X_train, X_test, y_train, y_test` |
| 类别不平衡仍只看 accuracy | 看 F1 / 精确率 / 召回率 / 混淆矩阵 |
| 用测试集调参 | 调参只用训练集 + 交叉验证 |
| `fit` 传了 y 给无监督模型 | 无监督只传 `X` |
| 忘记 `random_state` | 所有随机过程都固定种子，保证可复现 |
| 直接手写多步预处理 | 打包成 `Pipeline`，避免泄漏 |

---

## 小结

> ✅ **一句话结论**：scikit-learn 把传统机器学习统一成 `fit` / `predict` / `transform` 三个动作；一份完整实验的骨架永远是「先 `train_test_split` 划分、预处理只在训练集 `fit`、选模型 `fit` 后 `predict`、用 `classification_report` 或 `r2_score` 评估、需要时用 `GridSearchCV` 配 `Pipeline` 调参」，最容易翻车的三处是**测试集误 fit、无序特征乱编码、拿测试集调参**。
