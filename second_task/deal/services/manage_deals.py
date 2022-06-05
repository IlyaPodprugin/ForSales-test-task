import os

from fast_bitrix24 import Bitrix
from dotenv import load_dotenv

from .deal_userfields import DealStringUserField


load_dotenv()
WEBHOOK = os.getenv("WEBHOOK", False)
bitrix = Bitrix(WEBHOOK)


def get_contact(request, filter):
	contact = bitrix.get_all("crm.contact.list", params={"filter": filter})
	if contact:
		return contact[0]
	return None


def create_contact(request):
	contact_id = bitrix.call(
		"crm.contact.add", 
		items={
			"fields": {
				"NAME": request["client"]["name"],
				"LAST_NAME": request["client"]["surname"],
				"PHONE": [{"VALUE": request["client"]["phone"], "VALUE_TYPE": "MOBILE"}],
				"ADDRESS": request["client"]["adress"]
			}
		})
	if contact_id:
		return get_contact(request, {"ID": contact_id})
	return None
	

def add_new_contact(request):
	contact = create_contact(request)
	if contact:
		deal = create_deal(request, contact)
		if deal: 
			return {"crm.deal": deal, "crm.contact": contact}
		return "Deal was not created"
	return "Contact was not created"


def get_deal(request, filter):
	deal = bitrix.get_all(
		"crm.deal.list", 
		params={
			"select": ["TITLE", "SOURCE_DESCRIPTION", "CONTACT_ID", "UF_*"],
			"filter": filter
		})
	if deal:
		return deal[0]
	return None


def update_deal(request, deal_id):
	is_deal_updated = bitrix.call(
		"crm.deal.update",
		items={
			"id": deal_id,
			"fields": {
				"UF_CRM_DELIVERY_ADRESS": request["delivery_adress"],
				"UF_CRM_DELIVERY_DATE": request["delivery_date"],
				"UF_CRM_PRODUCTS": ", ".join(request["products"])
			}
		})
	if is_deal_updated:
		return get_deal(request, {"ID": deal_id})
	return None


def create_deal(request, contact):
	deal_id = bitrix.call(
		"crm.deal.add",
		items={
			"fields": {
				"TITLE": request["title"],
				"SOURCE_DESCRIPTION": request["description"],
				"CONTACT_IDS": contact,
				"UF_CRM_PRODUCTS": ", ".join(request["products"]),
				"UF_CRM_DELIVERY_ADRESS": request["delivery_adress"],
				"UF_CRM_DELIVERY_DATE": request["delivery_date"],
				"UF_CRM_DELIVERY_CODE": request["delivery_code"],
			}
		})
	if deal_id:
		return get_deal(request, {"ID": deal_id})
	return None


def add_new_deal(request, contact):
	deal = create_deal(request, contact)
	if deal: 
		return {"crm.deal": deal, "crm.contact": contact}
	return "Deal was not created"



def handle_request(request):
	# Установить необходимые пользовательские поля сделок, 
	# если они ещё не установлены
	deal = DealStringUserField(bitrix)
	deal.set_fields()

	# Проверка наличия контакта
	contact = get_contact(request, {"PHONE": request["client"]["phone"]})
	if not contact:
		return add_new_contact(request)

	# Проверка наличия сделки
	deal = get_deal(request, {"UF_CRM_DELIVERY_CODE": request["delivery_code"]})
	if not deal:
		return add_new_deal(request, contact)
	
	rules = (
		deal["UF_CRM_DELIVERY_ADRESS"] == request["delivery_adress"],
		deal["UF_CRM_DELIVERY_DATE"] == request["delivery_date"],
		all(product in deal["UF_CRM_PRODUCTS"].split(", ") for product in request["products"]),
	)

	# Если уже создан контакт и сделка, то скрипт сравнивает данные 
	# в запросе и сделке и, если что-то отличается, обновляет сделку
	if not all(rules):
		deal = update_deal(request, deal["ID"])
	return {"crm.deal": deal, "crm.contact": contact}
