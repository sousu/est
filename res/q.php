<html>
<head>
<?php
print "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=shift_jis\" />";
$path = htmlspecialchars($_GET['p'], ENT_QUOTES,'SJIS');
$base = '/est/';
$url = $base . $path;
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
