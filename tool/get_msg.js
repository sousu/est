//
// Outlook経由でのメールメッセージ情報抽出
//

//try {
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

//} catch(e){
//    WScript.echo(e);
//
//}

//各種データを取得
//
//Debug.Print "SentOnBehalfOfName: " & msg.SentOnBehalfOfName
//Debug.Print "SenderName: " & msg.SenderName
//Debug.Print "ReceivedByName: " & msg.ReceivedByName
//Debug.Print "ReceivedOnBehalfOfName: " & msg.ReceivedOnBehalfOfName
//Debug.Print "ReplyRecipientNames: " & msg.ReplyRecipientNames
//Debug.Print "To: " & msg.To
//Debug.Print "CC: " & msg.CC
//Debug.Print "BCC: " & msg.Bcc
//Debug.Print "Subject: " & msg.Subject
//Debug.Print "Body: " & msg.Body
//Debug.Print "HTMLBody: " & msg.HTMLBody
//'Debug.Print "Recipients: " & msg.Recipients
//Debug.Print "SenderEmailAddress: " & msg.SenderEmailAddress
//
//結果
//
//SentOnBehalfOfName: sender@example.jp
//SenderName: sender@example.jp
//ReceivedByName: 
//ReceivedOnBehalfOfName: 
//ReplyRecipientNames: sender@example.jp
//To: to@example.jp
//CC: 
//BCC: 
//Subject: 件名
//Body: 本文
//
//HTMLBody: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN">
//<HTML>
//<HEAD>
//<META NAME="Generator" CONTENT="MS Exchange Server version 14.02.5004.000">
//<TITLE></TITLE>
//</HEAD>
//<BODY>
//<!-- Converted from text/plain format -->
//
//<P>本文</P>
//
//</BODY>
//</HTML>
//
//SenderEmailAddress: sender@example.jp

