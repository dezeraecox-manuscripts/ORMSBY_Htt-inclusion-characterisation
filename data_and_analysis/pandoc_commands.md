
- To get reference.docx file (to then update templates)
pandoc --print-default-data-file reference.docx > reference.docx

- to convert word to md
pandoc -s Text_drafts/Draft_1 _manuscript.md -o Text_drafts/draft_1_manuscript.docx
