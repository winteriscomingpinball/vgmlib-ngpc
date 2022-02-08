@path=%PATH%;E:\ngpcdev\T900\BIN
@SET THOME=E:\ngpcdev\T900
@PROMPT $P$_NGPC$G
@make -B

@for /r %%x in (*.ngp) do python romsize.py "%%x"

@pause