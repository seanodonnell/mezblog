$(document).ready(function(){
tinyMCE.init(
  {
    mode:"exact",
    elements : "id_comment",
    theme: "advanced",
    theme_advanced_buttons1 : "bold, italic, underline,link,unlink",
    theme_advanced_buttons2 : "",
    theme_advanced_buttons3 : "",
    doctype: '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">',
    inline_styles: false,
    content_css : "/static/css/commenteditor.css",
    width: "528"
  });
}
);


