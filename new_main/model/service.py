# from .test_search import Agent
from .RAG import Agent

# 全局单例Agent实例，只初始化一次
_agent_instance = None

def _get_agent():
    """获取Agent单例实例"""
    global _agent_instance
    if _agent_instance is None:
        print("首次初始化Agent实例...")
        _agent_instance = Agent()
    return _agent_instance

# 将本函数替换为模型的入口函数
def answer(message, history):
    """
    回答用户问题
    
    Args:
        message: 用户消息
        history: 历史对话
        doc_type: 可选，指定只查询某种类型的文档。
                  例如 'Case' 只查案例，None 查所有类型
    """
    agent = _get_agent()
    return agent.query(message, history)
