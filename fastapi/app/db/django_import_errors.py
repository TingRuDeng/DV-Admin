class DjangoDataImportError(RuntimeError):
    """Django fixture 导入失败，必须中断流程并暴露根因。"""
