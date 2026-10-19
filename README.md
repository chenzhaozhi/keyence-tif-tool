# KeyenceTifTool

基恩士深度图（16bit TIFF）一键转 PNG/BMP 的 Windows 小工具。
拖 tif 文件/文件夹到 exe 上即可批量转换，自动 0.1%~99.9% 分位对比度拉伸（ImageJ Auto 风格），原图不动。

- 发布包：Actions Artifacts（build-exe 工作流）里的 `KeyenceTifTool-win64`
- 用法：把 .tif/.tiff 拖到 KeyenceTifTool.exe 上；或双击 exe 选文件/文件夹。命令行/拖放模式可用 `KeyenceTifTool.exe --bmp <文件或文件夹>` 同时输出 BMP。
- 窗口模式：勾选「同时输出 BMP」可同时输出 BMP，默认不勾选。
- 输出：默认仅输出同目录 `<原名>_stretched.png`；启用 BMP 后另输出 `<原名>_stretched.bmp`。
