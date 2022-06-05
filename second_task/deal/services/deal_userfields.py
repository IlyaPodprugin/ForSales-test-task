from typing import NoReturn


class DealStringUserField:
	"""
	Класс используется для работы с пользовательскими 
	полями сделок Битрикс24
	"""

	def __init__(self, bitrix) -> None:
		self.bitrix = bitrix

	def _set_userfield(self,
		field_name: str, edit_form_label: str, 
		list_column_label: str, xml_id: str, mandatory="Y"
	) -> int:
		"""Метод устанавливает пользовательское поле сделки"""
		return self.bitrix.call(
			"crm.deal.userfield.add",
			items={
				"fields": {
					"FIELD_NAME": field_name,
					"EDIT_FORM_LABEL": edit_form_label,
					"LIST_COLUMN_LABEL": list_column_label,
					"USER_TYPE_ID": "string",
					"XML_ID": xml_id,
					"MANDATORY": mandatory
				}
			})

	def _get_deal_fields(self) -> dict:
		"""
		Метод получает список полей сделок Битрикс24.
		Используется для проверки наличия необходимых 
		пользовательских полей
		"""
		return self.bitrix.call("crm.deal.fields", raw=True)

	def set_fields(self) -> NoReturn:
		"""
		Метод проверяет наличие необходимых пользовательских полей 
		и устанавливает недостающие
		"""
		fields: dict = self._get_deal_fields()

		if "UF_CRM_DELIVERY_ADRESS" not in fields:
			self._set_userfield(
				field_name="DELIVERY_ADRESS",
				edit_form_label="Адрес доставки",
				list_column_label="Адрес доставки",
				xml_id="DELIVERY_ADRESS"
			)
		if "UF_CRM_DELIVERY_CODE" not in fields:
			self._set_userfield(
				field_name="DELIVERY_CODE",
				edit_form_label="Код доставки",
				list_column_label="Код доставки",
				xml_id="DELIVERY_CODE"
			)
		if "UF_CRM_DELIVERY_DATE" not in fields:
			self._set_userfield(
				field_name="DELIVERY_DATE",
				edit_form_label="Дата доставки",
				list_column_label="Дата доставки",
				xml_id="DELIVERY_DATE"
			)
		if "UF_CRM_PRODUCTS" not in fields:
			self._set_userfield(
				field_name="PRODUCTS",
				edit_form_label="Продукты",
				list_column_label="Продукты",
				xml_id="PRODUCTS"
			)
