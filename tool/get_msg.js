//
// Outlook経由でのメールメッセージ情報抽出
//

try{
    var ol = new ActiveXObject('Outlook.Application');
    var fso = new ActiveXObject("Scripting.FileSystemObject");
    var f = WScript.Arguments(0);
    var msg = ol.CreateItemFromTemplate(fso.GetAbsolutePathName(f));

    WScript.echo("SentOnBehalfOfName: "+msg.SentOnBehalfOfName);
    WScript.echo("SenderEmailAddress: "+msg.SenderEmailAddress);
    WScript.echo("To: "+msg.to);
    WScript.echo("CC: "+msg.cc);
    WScript.echo("BCC: "+msg.bcc);
    WScript.echo("Subject: "+msg.Subject);
    WScript.echo(msg.Body);
} catch(e){
    WScript.echo(e);
}

