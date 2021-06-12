from dataclasses import dataclass, field


@dataclass
class XmlRequest:
    id: int = 0
    text: str = ''
    region_id: int = 0
    xml_url: str = ''
    validated_text: str = ''
    status: str = ''
    refresh_timer: int = 0
    reruns_count: int = 0
    bottom_ads_count: int = 0
    top_ads_count: int = 0


@dataclass
class RequestDataSet:
    id: int
    text: str
    xml: str
    xml_status: str
    region_id: int


@dataclass
class SiteDataSet:
    html: str = ''
    type: str = ''
    order_on_page: int = 1

    domain: str = ''
    invalid_domain_zone: bool = False
    domain_age: int = 0
    unique_backlinks: int = 0
    total_backlinks: int = 0
    backlinks_status: str = ''
    domain_group: int = 0

    content_letters_amount: int = 0
    content_stemmed_title: list = field(default_factory=lambda: [])
    is_content_valid: bool = False


@dataclass
class OrderDataSet:
    id: int
    actual_completition_percent: int
    stored_completition_percent: int