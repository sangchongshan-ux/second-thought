param([string]$Doc = "E:\ChatGPT\2026-11-11-13-35-39\a2-second-thought\docs\A2_Project_Report_3129594.docx")

# Counts the report the way Word's own word counter does, over the ranges the
# brief counts: the abstract, and the main report (sections 1-5 plus Table 1).
# Captions, references and front matter are outside both ranges.
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$d = $word.Documents.Open($Doc, $false, $true)
$d.Repaginate()

function FindStart($doc, $text, $matchCase) {
  $r = $doc.Content
  $f = $r.Find
  $f.Text = $text
  $f.Forward = $true
  $f.MatchCase = $matchCase
  $f.MatchWholeWord = $matchCase
  if (-not $f.Execute()) { throw "not found: $text" }
  return $r.Start
}

$absStart = FindStart $d "Abstract" $true
$bodyStart = FindStart $d "1. The problem" $false
$refStart = FindStart $d "References" $true

$absWords = $d.Range($absStart, $bodyStart).ComputeStatistics(0)
$bodyWords = $d.Range($bodyStart, $refStart).ComputeStatistics(0)

Write-Output ("WORD_ABSTRACT=" + $absWords)
Write-Output ("WORD_BODY=" + $bodyWords)
Write-Output ("WORD_COUNTED_TOTAL=" + ($absWords + $bodyWords))
Write-Output ("WORD_ALL_IN=" + $d.ComputeStatistics(0))
Write-Output ("PAGES=" + $d.ComputeStatistics(2))

$d.Close(0)
$word.Quit()
