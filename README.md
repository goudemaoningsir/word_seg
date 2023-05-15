<div align="center">
  <a href="https://github.com/sanmaomashi/word_seg">
    <img src="https://raw.githubusercontent.com/sanmaomashi/word_seg/main/img/1.jpg" height="400">
  </a>
  <h1>Word Segmentation</h1>
  <img src="https://img.shields.io/github/repo-size/sanmaomashi/word_seg.svg?label=Repo%20size&style=flat-square" height="20">
  <img src="https://img.shields.io/badge/License-Apache%202.0-purple" data-origin="https://img.shields.io/badge/License-Apache%202.0-blue" alt="">
</div>





## 简介

自然语言处理 分词服务

基于以下开源组件的 fastapi 实现：

- [PaddleNLP](https://github.com/PaddlePaddle/PaddleNLP/blob/develop/docs/model_zoo/taskflow.md#%E4%B8%AD%E6%96%87%E5%88%86%E8%AF%8D)

- [jieba](https://github.com/fxsjy/jieba)

- [HanLP](https://github.com/hankcs/HanLP)

- [JioNLP](https://github.com/dongrixinyu/JioNLP)

  



## 免责声明

本仓库为非盈利仓库，对任何法律问题及风险不承担任何责任。

本仓库没有任何商业目的，如果认为侵犯了您的版权，请来信告知。

本仓库不能完全保证内容的正确性。通过使用本仓库内容带来的风险与本人无关。



## 本地部署

1. 克隆项目

```bash
git clone https://github.com/sanmaomashi/word_seg.git
```

2. 安装依赖

```bash
pip install -r requirements -i https://mirror.baidu.com/pypi/simple
```

3. 执行项目

```bash
cd /项目目录/bin
bash start_project.sh
```

4. 访问swagger ui

```http
http://{{ip}}:1701/docs
```

![](https://raw.githubusercontent.com/sanmaomashi/word_seg_service/main/img/2.swagger.png)

## docker部署

构建镜像

```bash
docker build -t nlp:word_seg .
```

启动容器

```bash
docker run -d --name word_seg -p 1701:1701 --restart=always nlp:word_seg
```

访问swagger ui

```http
http://{{ip}}:1701/docs
```

![](https://raw.githubusercontent.com/sanmaomashi/word_seg_service/main/img/2.swagger.png)



## License

Licensed under the [Apache-2.0](http://choosealicense.com/licenses/apache/) © word_seg

