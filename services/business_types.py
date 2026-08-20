from __future__ import annotations

from dataclasses import dataclass

from services.business_type_catalog import NICHE_CATALOG


@dataclass(frozen=True)
class BusinessType:
    value: str
    label: str
    queries: tuple[str, ...] = ()
    included_type: str | None = None
    aliases: tuple[str, ...] = ()

    @property
    def search_terms(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys((self.label, *self.queries, *self.aliases)))


def _format_label(raw_label: str) -> str:
    if raw_label == "DJ":
        return raw_label

    lower_words = {"a", "e", "de", "do", "da", "dos", "das", "para"}
    words = raw_label.title().split()
    return " ".join(
        word.lower() if index and word.lower() in lower_words else word
        for index, word in enumerate(words)
    )


# `included_type` is only used for values accepted by the Places API Table A.
# Product categories without an official equivalent rely on their text queries.
OFFICIAL_BUSINESS_TYPES: tuple[BusinessType, ...] = (
    BusinessType("restaurant", "Restaurante", included_type="restaurant", aliases=("comida", "refeicao")),
    BusinessType("pizza_restaurant", "Pizzaria", included_type="pizza_restaurant", aliases=("pizza",)),
    BusinessType("hamburger_restaurant", "Hamburgueria", included_type="hamburger_restaurant", aliases=("hamburguer", "burger")),
    BusinessType("brazilian_restaurant", "Restaurante Brasileiro", included_type="brazilian_restaurant", aliases=("brasileira", "brasileiro")),
    BusinessType("barbecue_restaurant", "Churrascaria", included_type="barbecue_restaurant", aliases=("churrasco", "barbecue")),
    BusinessType("seafood_restaurant", "Frutos do Mar", included_type="seafood_restaurant", aliases=("peixaria", "frutos do mar", "camarao")),
    BusinessType("steak_house", "Steakhouse", included_type="steak_house", aliases=("churrascaria", "steak")),
    BusinessType("fast_food_restaurant", "Fast Food", included_type="fast_food_restaurant", aliases=("lanchonete rapida",)),
    BusinessType("sandwich_shop", "Lanchonete", included_type="sandwich_shop", aliases=("lanche", "sanduiche")),
    BusinessType("bakery", "Padaria", included_type="bakery", aliases=("pao", "confeitaria")),
    BusinessType("cafe", "Café", included_type="cafe", aliases=("cafeteria",)),
    BusinessType("coffee_shop", "Cafeteria", included_type="coffee_shop", aliases=("cafe", "coffee")),
    BusinessType("bar", "Bar", included_type="bar", aliases=("boteco", "pub")),
    BusinessType("ice_cream_shop", "Sorveteria", included_type="ice_cream_shop", aliases=("sorvete", "acai")),
    BusinessType("barber_shop", "Barbearia", included_type="barber_shop", aliases=("barbearia", "barbeiro")),
    BusinessType("beauty_salon", "Salão de Beleza", included_type="beauty_salon", aliases=("salao", "beleza", "estetica")),
    BusinessType("hair_salon", "Cabeleireiro", included_type="hair_salon", aliases=("cabelo", "cabeleireira")),
    BusinessType("nail_salon", "Manicure", included_type="nail_salon", aliases=("unha", "nail")),
    BusinessType("spa", "Spa / Estética", included_type="spa", aliases=("spa", "estetica", "clinica de estetica")),
    BusinessType("pharmacy", "Farmácia", included_type="pharmacy", aliases=("drogaria", "remedio")),
    BusinessType("doctor", "Clínica / Consultório", included_type="doctor", aliases=("medico", "clinica", "consultorio")),
    BusinessType("medical_clinic", "Clínica Médica", included_type="medical_clinic", aliases=("clinica medica",)),
    BusinessType("dentist", "Dentista", included_type="dentist", aliases=("odontologia", "dente")),
    BusinessType("dental_clinic", "Clínica Odontológica", included_type="dental_clinic", aliases=("odontologica", "odontologia")),
    BusinessType("physiotherapist", "Fisioterapeuta", included_type="physiotherapist", aliases=("fisioterapia",)),
    BusinessType("veterinary_care", "Veterinária", included_type="veterinary_care", aliases=("vet", "veterinario", "clinica veterinaria")),
    BusinessType("gym", "Academia", included_type="gym", aliases=("fitness", "musculacao")),
    BusinessType("clothing_store", "Loja de Roupas", included_type="clothing_store", aliases=("roupa", "moda", "boutique")),
    BusinessType("shoe_store", "Loja de Sapatos", included_type="shoe_store", aliases=("calcado", "sapato")),
    BusinessType("supermarket", "Supermercado", included_type="supermarket", aliases=("mercado",)),
    BusinessType("grocery_store", "Mercearia", included_type="grocery_store", aliases=("armazem",)),
    BusinessType("convenience_store", "Conveniência", included_type="convenience_store", aliases=("loja de conveniencia",)),
    BusinessType("pet_store", "Petshop", included_type="pet_store", aliases=("pet shop", "pet", "banho e tosa")),
    BusinessType("electronics_store", "Eletrônicos", included_type="electronics_store", aliases=("informatica", "celular")),
    BusinessType("furniture_store", "Móveis", included_type="furniture_store", aliases=("moveis", "decoracao")),
    BusinessType("jewelry_store", "Joalheria", included_type="jewelry_store", aliases=("joia", "otica e joalheria")),
    BusinessType("florist", "Floricultura", included_type="florist", aliases=("flor", "flores")),
    BusinessType("lawyer", "Advocacia", included_type="lawyer", aliases=("advogado", "escritorio de advocacia")),
    BusinessType("accounting", "Contabilidade", included_type="accounting", aliases=("contador", "contabil")),
    BusinessType("real_estate_agency", "Imobiliária", included_type="real_estate_agency", aliases=("imovel", "corretor")),
    BusinessType("insurance_agency", "Seguros", included_type="insurance_agency", aliases=("seguradora", "corretor de seguros")),
    BusinessType("car_repair", "Oficina Mecânica", included_type="car_repair", aliases=("mecanica", "auto center", "oficina")),
    BusinessType("car_dealer", "Concessionária", included_type="car_dealer", aliases=("revenda de carros", "automoveis")),
    BusinessType("car_wash", "Lava-rápido", included_type="car_wash", aliases=("lava rapido", "estetica automotiva")),
    BusinessType("hardware_store", "Material de Construção", included_type="hardware_store", aliases=("construcao", "reforma", "ferragem")),
    BusinessType("electrician", "Eletricista", included_type="electrician", aliases=("eletrica",)),
    BusinessType("plumber", "Encanador", included_type="plumber", aliases=("hidraulica", "bombeiro hidraulico")),
    BusinessType("school", "Escola", included_type="school", aliases=("colegio", "educacao")),
    BusinessType("preschool", "Escola Infantil", included_type="preschool", aliases=("creche", "infantil")),
    BusinessType("hotel", "Hotel", included_type="hotel", aliases=("pousada", "hospedagem")),
    BusinessType("laundry", "Lavanderia", included_type="laundry", aliases=("lavagem",)),
    BusinessType("travel_agency", "Agência de Viagens", included_type="travel_agency", aliases=("turismo", "viagem")),
    BusinessType("gas_station", "Posto de Combustível", included_type="gas_station", aliases=("posto", "gasolina")),
)


NICHE_BUSINESS_TYPES = tuple(
    BusinessType(
        value=value,
        label=_format_label(label),
        queries=queries,
        included_type=included_type,
    )
    for value, label, queries, included_type in NICHE_CATALOG
)


_types_by_value = {item.value: item for item in OFFICIAL_BUSINESS_TYPES}
_types_by_value.update({item.value: item for item in NICHE_BUSINESS_TYPES})
BUSINESS_TYPES: tuple[BusinessType, ...] = tuple(_types_by_value.values())


def get_business_type(value: str) -> BusinessType | None:
    return _types_by_value.get(value)


def as_dicts() -> list[dict[str, str | list[str]]]:
    return [
        {"value": item.value, "label": item.label, "aliases": list(item.search_terms)}
        for item in BUSINESS_TYPES
    ]


def type_labels() -> dict[str, str]:
    return {item.value: item.label for item in BUSINESS_TYPES}
