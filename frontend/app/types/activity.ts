export type ActivityAction = 'created' | 'updated' | 'deleted' | 'status_changed' | 'auto_generated'
export type ActivityEntity =
  | 'wedding'
  | 'guest'
  | 'gift'
  | 'checklist'
  | 'vendor'
  | 'kua_document'
  | 'mahar_item'
  | 'cortage'
  | 'transaction'
  | 'savings_target'
  | 'order'
  | string
