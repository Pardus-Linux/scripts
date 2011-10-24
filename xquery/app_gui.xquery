<html>
<body style="width:1000px">
<table>
{
  for $v in /PISI/SpecFile/Source
  where $v/IsA = "app:gui"
  order by concat($v/PartOf,".",$v/Name) ascending
  return
  <tr>
    <td style="width:260px; border-bottom:1px solid black">{ concat($v/PartOf,".",$v/Name) }</td>
    <td style="width:150px; border-bottom:1px solid black">{ $v/Packager/Name }</td>
    <td style="width:540px; border-bottom:1px solid black">
    {
      for $d in $v/BuildDependencies/Dependency
      return concat($d/text()," " )
    }
    </td>
  </tr>
}
</table>
</body>
</html>

