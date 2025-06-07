from langchain.chains import LLMChain
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from langchain_community.callbacks import get_openai_callback
from riskgpt.utils.prompt_loader import load_prompt
from riskgpt.utils.memory_factory import get_memory
from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import CategoryRequest, CategoryResponse, ResponseInfo
from riskgpt.registry.chain_registry import register


@register("get_categories")
def get_categories_chain(request: CategoryRequest) -> CategoryResponse:
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_categories")


    template = prompt_data["template"]
    parser = PydanticOutputParser(pydantic_object=CategoryResponse)
    memory = get_memory(settings)
    model = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        temperature=settings.TEMPERATURE,
        model=settings.OPENAI_MODEL_NAME
    )

    format_instructions = parser.get_format_instructions()
    format_instructions = format_instructions.replace('{', '{{').replace('}', '}}')

    prompt = ChatPromptTemplate.from_template(
        template=template,
        partial_variables={"format_instructions": format_instructions}
    )

    inputs = request.model_dump()
    inputs["domain_section"] = f"Domain knowledge: {request.domain_knowledge}" if request.domain_knowledge else ""

    chain = prompt | model | parser
    with get_openai_callback() as cb:
        result = chain.invoke(inputs, memory=memory)
        result.response_info = ResponseInfo(
            consumed_tokens=cb.total_tokens,
            total_cost=cb.total_cost,
            prompt_name="get_categories",
            model_name=settings.OPENAI_MODEL_NAME
        )
    return result
