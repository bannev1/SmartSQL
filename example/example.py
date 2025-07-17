from ..query import SmartSQL

tableLayout = {
			"order_general_info": ""
		}

exp = SmartSQL(tableLayout, debug=True)

print(exp.query(['order_general_info'], "List all the orders of the past month"))
