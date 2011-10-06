function ui_dumpSortList(id) {
  res = '';
 
  List = document.getElementById(id);
  for (i=0; i<List.children.length; i++)
    res += '|' + List.children[i].id;
 
  return res.substr(1)
  
}
