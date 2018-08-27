// file reader/writer at UTF8
//  ref.http://d.hatena.ne.jp/miya2000/20100510/p0 

function readUTF8(filename){
    try {
        var adReadAll  = -1; // 全行
        //var adReadLine = -2; // 一行ごと
        var stream = new ActiveXObject("ADODB.Stream");
        stream.Type = 2;
        stream.Charset = "UTF-8";
        stream.Open();
        stream.LoadFromFile(filename);
        var tmp = stream.ReadText(adReadAll);
        stream.Close();
        return tmp;
    }
    finally {
        if (stream) try { stream.Close(); } catch(e) {}
    }
}
function writeUTF8(filename, text){
    try {
        var stream = new ActiveXObject("ADODB.Stream");
        //write text to stream as UTF-8.
        stream.Type = 2;
        stream.Charset = "UTF-8";
        stream.Open();
        stream.WriteText(text);
        //set position at 0 to change type(error occurs).
        stream.Position = 0;
        stream.Type = 1;
        //skip bom and read all bytes.
        stream.Position = 3;
        var bytes = stream.Read();
        //reset stream and write bytes.
        stream.Position = 0;
        stream.SetEOS();
        stream.Write(bytes);
        //save.
        stream.SaveToFile(filename, 2);
    }
    finally {
        if (stream) try { stream.Close(); } catch(e) {}
    }
}
