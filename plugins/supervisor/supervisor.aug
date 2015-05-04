module Supervisor =

let comment = 
    IniFile.comment /[#;]/ "#"

let title_comment = 
    [ label "#titlecomment" . del /[ \t]*[#;][ \t]*/ " # " . store /[^ \t\r\n]([^\r\n]*[^ \t\r\n])?/ ]

let title_noeol (kw:regexp)
    = Util.del_str "[" . key kw . Util.del_str "]" . title_comment? . Util.eol


let indented_title_noeol (kw:regexp)
   = Util.indent . title_noeol kw

let entry_generic_nocomment (kw:lens) (sep:lens)
                            (comment_re:regexp) (comment:lens) =
     let bare_re_noquot = (/[^ \t\r\n]/ - comment_re)
  in let bare_re = (/[^\r\n]/ - comment_re)+
  in let no_quot = /[^"\r\n]*/
  in let bare = (store (bare_re_noquot . (bare_re* . bare_re_noquot)?))
  in [ kw . sep . (Sep.opt_space . bare)? . (comment|Util.eol) ]

let entry_generic (kw:lens) (sep:lens) (comment_re:regexp) (comment:lens) =
  entry_generic_nocomment kw sep comment_re comment | comment

let indented_entry (kw:regexp) (sep:lens) (comment:lens) =
     entry_generic (Util.indent . key kw) sep IniFile.comment_re comment


let sep        = IniFile.sep "=" "="
let entry      = indented_entry IniFile.entry_re sep comment
let title      = indented_title_noeol IniFile.record_re
let record     = IniFile.record title entry
let lns        = IniFile.lns record comment
let filter = (incl "/etc/supervisor/supervisord.conf") . Util.stdexcl
let xfm = transform lns filter
