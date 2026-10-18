"""Typed arguments and tool-result fidelity checks; all tools are synthetic."""
def tool(name,properties,required):
 return {'name':name,'description':'合成測試工具，無外部操作：'+name,'parameters':{'type':'object','properties':properties,'required':required,'additionalProperties':False}}
TOOLS=[
 tool('create_draft',{'title':{'type':'string'},'items':{'type':'array','items':{'type':'object','properties':{'sku':{'type':'string'},'quantity':{'type':'integer'}},'required':['sku','quantity'],'additionalProperties':False}},'dry_run':{'type':'boolean'}},['title','items','dry_run']),
 tool('lookup_ticket',{'ticket_id':{'type':'string'}},['ticket_id']),
 tool('get_balance',{'account':{'type':'string'}},['account']),
 tool('search_docs',{'query':{'type':'string'}},['query']),
 tool('fetch_document',{'id':{'type':'string'}},['id']),
 tool('calculate_price',{'amount':{'type':'number'},'quantity':{'type':'integer'},'currency':{'type':'string','enum':['TWD','USD']}},['amount','quantity','currency'])]
CASES=[
 ('typed_nested','請使用 create_draft 建立模擬草稿，title 為「測試訂單」，items 只含一項 sku「TW-0042」、quantity 整數 3，dry_run 為布林 true。只輸出 JSON，鍵名 draft_id。',[('create_draft',{'title':'測試訂單','items':[{'sku':'TW-0042','quantity':3}],'dry_run':True},{'draft_id':'D-09Z'})],{'draft_id':'D-09Z'}),
 ('id_fidelity','請用 lookup_ticket 查 ticket_id「T-00O1lI-09Z」，保留大小寫與零，不得改寫。只輸出 JSON，鍵名 ticket_id、status。',[('lookup_ticket',{'ticket_id':'T-00O1lI-09Z'},{'ticket_id':'T-00O1lI-09Z','status':'處理中'})],{'ticket_id':'T-00O1lI-09Z','status':'處理中'}),
 ('permanent_error','請用 get_balance 查帳戶「A-0042」。若工具回傳不可重試的錯誤，立即停止，不得重試或捏造。只輸出 JSON，鍵名 balance，無法取得時為 null。',[('get_balance',{'account':'A-0042'},{'error':'permission_denied','retryable':False})],{'balance':None}),
 ('search_fetch','先用 search_docs 搜尋精確字串「備份政策」，再用 fetch_document 讀取工具回傳的 document_id，不得猜 ID。只輸出 JSON，鍵名 retention_days。',[('search_docs',{'query':'備份政策'},{'document_id':'DOC-00B7'}),('fetch_document',{'id':'DOC-00B7'},{'retention_days':37})],{'retention_days':37}),
 ('typed_numbers','請呼叫 calculate_price，amount 為數字 1299.5，quantity 為整數 2，currency 為字串 TWD。只輸出工具回傳 total 的 JSON，鍵名 total。',[('calculate_price',{'amount':1299.5,'quantity':2,'currency':'TWD'},{'total':2599})],{'total':2599}),
 ('no_tool','這題不需要工具，而且禁止呼叫任何工具。只原樣輸出 JSON：{"ready":true,"mode":"dry_run"}。',[],{'ready':True,'mode':'dry_run'})]
