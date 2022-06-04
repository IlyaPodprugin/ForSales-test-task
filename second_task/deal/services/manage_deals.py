import os

from fast_bitrix24 import Bitrix
from dotenv import load_dotenv


load_dotenv()
WEBHOOK = os.getenv("WEBHOOK", False)
bitrix = Bitrix(WEBHOOK)


def set_userfields(request):
	products = bitrix.call(
		"crm.deal.userfield.add",
		items={
			"fields": {
				"FIELD_NAME": "PRODUCTS",
				"EDIT_FORM_LABEL": "Продукты",
				"LIST_COLUMN_LABEL": "Продукты",
				"USER_TYPE_ID": "string",
				"XML_ID": "PRODUCTS",
				"MANDATORY": "Y"
			}
		})

	delivery_adress = bitrix.call(
		"crm.deal.userfield.add",
		items={
			"fields": {
				"FIELD_NAME": "DELIVERY_ADRESS",
				"EDIT_FORM_LABEL": "Адрес доставки",
				"LIST_COLUMN_LABEL": "Адрес доставки",
				"USER_TYPE_ID": "string",
				"XML_ID": "DELIVERY_ADRESS",
				"MANDATORY": "Y"
			}
		})

	delivery_date = bitrix.call(
		"crm.deal.userfield.add",
		items={
			"fields": {
				"FIELD_NAME": "DELIVERY_DATE",
				"EDIT_FORM_LABEL": "Дата доставки",
				"LIST_COLUMN_LABEL": "Дата доставки",
				"USER_TYPE_ID": "string",
				"XML_ID": "DELIVERY_DATE",
				"MANDATORY": "Y"
			}
		})

	delivery_code = bitrix.call(
		"crm.deal.userfield.add",
		items={
			"fields": {
				"FIELD_NAME": "DELIVERY_CODE",
				"EDIT_FORM_LABEL": "Код доставки",
				"LIST_COLUMN_LABEL": "Код доставки",
				"USER_TYPE_ID": "string",
				"XML_ID": "DELIVERY_CODE",
				"MANDATORY": "Y"
			}
		})
	
	return products, delivery_adress, delivery_date, delivery_code


def get_contact(request, filter):
	contact = bitrix.get_all("crm.contact.list", params={"filter": filter})
	if contact:
		return contact[0]
	return None


def get_deal(request, filter):
	deal = bitrix.get_all(
		"crm.deal.list", 
		params={
			"select": ["TITLE", "SOURCE_DESCRIPTION", "UF_*"],
			"filter": filter
		})
	if deal:
		return deal[0]
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
	

def handle_request(request):
	contact = get_contact(request, {"PHONE": request["client"]["phone"]})

	if not contact:
		contact = create_contact(request)
		if contact:
			deal = create_deal(request, contact)
			if deal: 
				return {"crm.deal": deal, "crm.contact": contact}
			return "Deal was not created"
		return "Contact was not created"

	deal = get_deal(request, {"UF_CRM_DELIVERY_CODE": request["delivery_code"]})
	if not deal:
		deal = create_deal(request, contact)
		if deal: 
			return {"crm.deal": deal, "crm.contact": contact}
		return "Deal was not created"
	
	rules = (
		deal["UF_CRM_DELIVERY_ADRESS"] == request["delivery_adress"],
		deal["UF_CRM_DELIVERY_DATE"] == request["delivery_date"],
		all(product in deal["UF_CRM_PRODUCTS"].split(", ") for product in request["products"]),
	)

	if not all(rules):
		deal = update_deal(request, deal["ID"])
	return {"crm.deal": deal, "crm.contact": contact}
