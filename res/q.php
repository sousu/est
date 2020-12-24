<html>
<head>
<?php
$path = rawurldecode($_GET['p']);
$path = mb_convert_encoding($path,'UTF-8','SJIS');
$url = '/est/' . $path;
//echo $url;
?>
<title>Redirect ...</title>
<?php echo "<meta http-equiv=\"Refresh\" content=\"0; URL=".$url."\">"; ?>
<script type="text/javascript">
function selfclose() {
    (window.open('', '_self').opener = window).close();
}
window.setTimeout("selfclose();",10000);
</script>
</head>
<body>

</body>
</html>
