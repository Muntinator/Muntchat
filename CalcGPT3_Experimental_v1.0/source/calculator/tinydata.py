# CalcGPT 3 model installer 1 of 8. Run in order.
MODEL_ID=1282619148
BUILD=2
from ti_system import store_list,recall_list
FORMAT=13
ALPHABET="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~"
def decode(blob,length):
 out=[]
 for start in range(0,len(blob),5):
  value=0
  for ch in blob[start:start+5]: value=value*85+ALPHABET.index(ch)
  out.extend(((value>>24)&255,(value>>16)&255,(value>>8)&255,value&255))
 return out[:length]
def checksum(values):
 a=1; b=0
 for value in values:
  a=(a+value)%65521
  b=(b+a)%65521
 return (b<<16)|a
def installed(stage):
 try: marker=recall_list("tds"+str(stage))
 except Exception: return False
 return len(marker)>0 and int(marker[0])==MODEL_ID
def install(name,length,signed,blob,expect):
 values=decode(blob,length)
 if checksum(values)!=expect:
  print("Checksum failed for",name,"- re-paste this program"); raise SystemExit
 if signed:
  for j in range(len(values)):
   if values[j]>127: values[j]-=256
  pairs=[]
  for j in range(0,len(values),2):
   first=values[j]+128
   second=values[j+1]+128 if j+1<len(values) else 128
   pairs.append(first*256+second)
  values=pairs
 store_list(name,values)
 if len(recall_list(name))!=len(values):
  print("Verification failed for",name,"- re-paste this program"); raise SystemExit
def verify(prefix,count,length,expect):
 a=1; b=0; seen=0
 for part in range(count):
  for packed in recall_list(prefix+str(part)):
   packed=int(packed)
   for value in ((((packed>>8)-128)&255),(((packed&255)-128)&255)):
    if seen>=length: break
    a=(a+value)%65521
    b=(b+a)%65521
    seen+=1
 if seen!=length:
  print("Incomplete model part",prefix); raise SystemExit
 if (b<<16)|a!=expect:
  print("Corrupt model part",prefix); raise SystemExit

try:
 existing=recall_list("tdinfo")
except Exception:
 existing=[]
if len(existing)>7 and int(existing[0])==FORMAT and int(existing[7])==MODEL_ID:
 pasted=input("CalcGPT is installed. Paste text for it, then press Enter: ")
 store_list("tdpaste",[ord(ch) for ch in pasted[:120]])
 print("Paste saved. Run CalcGPT.")
 raise SystemExit
if len(existing)>7 and int(existing[0])==FORMAT and int(existing[7])!=MODEL_ID:
 reply=input("A different CalcGPT model is installed. Replace it? (y/n): ")
 if reply.strip().lower()!="y":
  print("Installation cancelled. Existing model left untouched.")
  raise SystemExit
install('tdq0x0',1600,1,'1`6B)<Ln{#=;{Fi0~rbL_yqbD?(_x)1pgQW{`mF^4-5(l1rP!N842k33-{;<^8ok(;|dV_<MaCj`uNouKEf{)`1S}196Rt4*Yz&^{w7Gi=?T;m5bBuFpQ{xeA}p^k?(6sL+u|A^wh-zTrv@3@_SO9*!wvWe67b>w1o{Qt^eynl2@ewk@+AYo^b!KlC;#Iw`XTxm88O-_?)K^O9X|IU6%`!V>H0Ye^d<r@)awlq2MFl?6BOgz>?#cP><JeX^&%nU`Q-Qu?Lor@5AW*ZwGs9x(KZ7D4Hz~D0wDzvA^rIz3@^h585-3B4)Zb$;_W2&OxP72*CWmj1p@u|)X6<72R8}&2ITY&3m7u=+7%uM`UMB<>kAPY^XLWZxE?bA)(`IQ=j0{~>LN1t2IuSk%^LpmzBLT-1Pl)S<QwfV3km=J`6>Gk;t&7(0p}C;_ZAun4dxN&03_2J@C^Rt5AXHm7bVUD{{bip4d&<?)a4Kh@C?cgA_Mfc1r{Ru0{sIV3F`_24(%i56)E@)@d5}h`XKZ2&8`352@U`82=@fZ+a47c2nqZUB=+qJ{pQ{82Ok&{7z+*B_$c}e^bhC&;u789-}VaL?&b~s&g=Q@{{;mH)GG7e^$`y9A^zp}-scPzEcf;4@FMo~{sbxr020*v66f*x{SgHM3;!Sw_Xr9E+6@9I2JHP4A_Vv+81nh`1|AO-76=&K;S~n$@E!B<0}><;KlcLF>;wK2?CK~G6cGIE3e5la0sQkH0tn;*-UUH05a!|y<ox~gA>!%<<nR~_(GmRr?&=L22<#W+9~kok{tD#?+yEi%A|3eu4d}uI#sLBC76l$5_R#J3;r9*y>HXCd6Z{46=maq%|0L@(<Rt#z5(d-R5Eu|I2m#v(0P6ek_y*Yr_u2LPA1wt05A^2Q{tN>0^bzm#1?mF;{TliU6Z91a0SnL}<Nyr`-UZkr91R5D>isbh2m<~(@y`G5671g)6XpBi5*!E1@Fe*P72OL4=I;FO59R766!izU1mXqd9u5N;=LiA#3K{tJ_x1Gj*!1)C3m)s&^6DDw{~O*h=<d}c1PMSZ4*~r6^#BP4^a|q!^C0pO_}&W?@Zu37{rc|*_7D%>-RbQ3`R@`61Pt~m0Q3yz4B_ww;qwas-w6W;@c0lK04M9+3+dS;;R+NC%=7;H1p3?q9Si{a_3;Ps@!s4DM&<Yt=I%BB1pL?b4<jSn$pQQK?A!tl1Of;8@&Opu5Dx3|`WW#X-vku%8r2Q>=@s}D6&D8+`~C3e^!MoF`r{D)Gtu7t`y31V;qnOl<_|F6@bMxK8vE$c+7kKr?ja8N;|C508saDM-w5;RD+UAj4HX!}03GcP3k>D^BnAEB!`%M@3laqF^7{-M3-t>G?#=%BAP^hjFvS<f3Iibm1q2Zu*W(cR0^ZZ`Is)(a2Nm`a^#m6#?Gp|-`3wB}5g_m32qWVb^a}I*8Tt7A762q8@e=zQ>HP5HEcEO075NJY|N8Us`3b}H68!t_=>*F8?gH`c0ooVz)fyEy<M9v)<O&M~0xbdR{VEJ13IO^283G>i;tvG;*a;2^C<iGD8QU2M=^^a=8T|4F>G>ZZ_VWD@6z|^;8xigl3nTLN2N(C%0xI$p3hNmHA_ec;<mU|%59R~q%osQ7{o?@$`|kny<Np8&4G#+cI{o$k^Skly8vNtt<LLn}=nMn&{RIg80U7lI@$De_<njsnCFS}A4)j|L=@=Rs9P#M{?*6Su)BF<z{Q?yU?i1?r6$$<t3hy2c+}zMK1QGux1`!O{4(#&kDfH1A0tfyI2o=f$`}XDq?h_XDCF1J~AP^MF;0pQ`>l^n7^ZfV(`|1D&5)=*+_WKd{Bo+z`0rvY35cmxo#}WhR1Rd)P@d)Pl{1XcW`RwZN-uLwX6d^MH6awuN5*f<+?f}94G2#4A0><nB{wD0p<ObE!76|$G4=Cg1`vw6L3FZnX2nO#92-WBg0UG|&BK;lYz1Jc4K>8CC67>li6YB8V1~3N;6#NkF2mACY><Aa~_4eue67Uh?_BId(Fa!q;',3017476135)
install('tdq0x1',1600,1,'=ko6gA_DT~+z|uf>>wKK+w&mn?fC`v0Ok$x@EiynA^s8o{}A03{|)Bs=o16k^9%_S@dx7i4guiY;R^dS<OuTr1qkU0@(k+mCkG$@?fTjH@(>LJCIH_C5*FS93kCiV5fTO!9P<?eBMICR{{tlK9QGvZ;r|u?6aNhP^yK#K6ba%4D-H$+1sL%w_Z18H@CW_)5C{tj+YS=<>k<tW7Yx<a@CpR{`~2zh2<qP#1@aOW#}fVQ7Z~II><8%h5Cs(vA_wyp`1BAG1_U4=A_wy7A^GL$E7Il$<?#qBCGz?Z{Sy(*|Nr~^*Z36eC(A$M3IGThA>-oi1?RaJCV}J-@(~2#9tZ;B2FwuKBQ*d+75)VQ8ul6h`v&kC2O#SK;Q<XR-XHMr5CQ4z4i_US0t4X#2H^qY;Slfk2pj_d1_0&Z<N+}G`3vU{2;l@O^5hl#`|be}|LF??_WKq4`P&);@!0_K>fPx00}2iQ0q*we<LvSP;OXHP5e)jz`~WWy1Qqov4CL$~;|~!07xvHn?*auP)9wxU8P5Y3*Xbb9_x;{0A?yqvCk62g3jOI86d?8Q+3qzL>Im)8_#!0>^Az;-DG2`Y7X36V^$G+N%;W6}AJ_Ex+T6x63>y|x6#*3$MGRR+)gv1^4e9>y0UihB`4H^w5zpE$<Ld|{<`DV!<q9AG@Zta!`}qM50{Q_A0qpR`2`w27AO`}||MUDI+W+O|1ql<~`xYbz0yHon3;*;V<@@(3-Z&EZ`UVR91rrMf<Le6q76$7H_U;-U7zG<7Ap!LLIpON(;o24m;~3Zq8U_^g-zy9M4j>5y(IWs-7xLQ&^!N_{1_s&d6X^aE5&Zt{{{#>P1po2z>J#l80r?je>f!1^!p!3Q;r=A>^Ay+&5G3LZ75oC```04_|M%|>2n^Tx;SUWe?gtF!68;6~9t$TI>j~%Y4f*!#2=oUi7Vho{C+!3r0_)@C7YNQO2Lu)w{|e{`DFgrw?GXa<4iM@Q+4=YI*}Tx_>G~Vy(-6}q(E$0>M?3WJ2L~h01qmoS>I(Va?<W-hL<jBd;`jvO_7L&y<|yzX3l$*dE&>M|-v|8x^aIHO1Ps>N1Mu$__2~%{;rR6`9su9?`4JfQAod6d&=Cd^;T-(-`4I^G<Pg*u2JI#H_R--R5B&QY-vR*<&;bP|{15;Z?c(wb0`&6>@AVW4AOHaN8}bDc>)h1s@gVgK7y|PHCnOpC85If)4gLlT-vads{PE{C3Lxys76{w$@+Kty-W~|w4-o<Y0u(vo?B4toDee2=1p~+~6Y}p)@B1JSGYRte^%@}g>lN?c0R8q1{PzV9;PVOb75n}E>FNpg3EbHrBNz1W0v7G@xh@9@5F88U3?2g?`35ZI5IX}F^XMDv>=N|)BGVQV_v!xR3hL_q>J0Y^_WThI1poOF8T<?W{rB+s?gSbx7}xOT3i${f@*n8&5B4q){tNf>=-(ss{SX7~6bcgt4Ghus1NZLo*d6uT{PqF;4fhN0=m{zV2>0at5E$C}`}7_i;Q|->;PB_i>K6Gi%;wSv<^~28DID+Z`zFsM1_1R5`Tpqx0qWlZ@9Zc02`dE~=-eCg?H>E?0q^+N4=4ikBkctH_8K7%B-{81Qwsv?5$xp2=>y#G_5k$_0tfaK{qy<&_znBg{r3O-2><T~+z$g47Ub>*2mjgW>jnq#{n))b0nNSi4(t*g!yZl?Hz%(i75@?r=KLxJ4*2{05fu*j`t$e^0tomE2-6S*`T*z$9~kZcBpK`k4;vN<3Fi#-7zg?E10DVB|M>9^`s*6?^cfK23Geay1QQSh7WeiC0R#iz3itZ->*Cq=76tqB5a8nP{vGrE<mVdr009i@+aLfF{xUG|^!pv#1mgw@9_AYZ5$7ub@CzR5_BIMX$_N+yB;fk!?F|9u8WrgH`~NK;3j4_B+9Dg>;1dn_>GbmO`t|el@e(EB86yH2<ptUY75~NZ@&yY7^z7L%_4Ei51q}P?Ch+VD0s9a81nTPF1qJ{205ACW9Sa%}9R2w30QwEm>D>4F0}&Pp2HO?=',766839077)
install('tdq0x2',1600,1,'1-=9s^A8Fo2k`0xBM1Eo3jzoY66f11>*LrH_TKd_HtX*B1N8s>_vj-BD(Le87qtN0=^P0D>jwt#3l9a|FbD|^@5~11`xPYPCEc<SCHw9n+y52w`r#Dp1qKWH?A;aZ1{LlW&GGyq2G<7`2Lb{0{tfQ$^$z{}<L>$X{`lMh2jC0!0}k;A3HCN4>g)9HAIcu>+9na%1`!GM4etj2@$nq^1o8d`{rLG3A^!dT^zjfH?G)tK>Gu@@?gaD(*~SX=1n}wD74G}`4;Ks@DGdJ%^9b$m@(JPZDE<cg5)C#L1PmP*`ThC<{}B2L_u&Hu0|EXF4($)~_8avECG_bM2I~3;9SZ#Z-y#jm6c7XF_4WM;4C@a52J;C981?@B3H%Ba4eagz|LzIt?*#B3?*!iU4IS$c4F4MUD%b(-2OiP_6#C^2<oV(e^8@qD_x%VD8U+OO_YDl|<tidm=mYKg@);El3K97S2OuN?1`poi49Fw*+U)Z3^7sAJ0w(<+E)MYv-`evR^7Q)J^Y!xZ0~YcL0|O=169?V;2lxo-01f>B<}v&92M6E)!uIVL1Psx{>lx(n$`T{?1l}zr5+VEU1Pk%q8zdbS^Z)Z3|Nrak^9wBX*CYSj6Al>#4+|9d=Isv??+Wei>F4?(1=ivxF(UTt8~GUr{ov;U@)G0>1@zwX1N`*#CL8?P8}~f|6%Zlr{rdU%4JFjl02B-F>h<dx0SyY|0r2w;5C{SN=?fbH10@;d<l6=Z;OF-95ZmeQ76vNu@&gjy?*s|s9{=(E5aAE~5ESp^``Ypq_V)Pr==J^@2MYlp6A%RV1R?ek+WqtH4eTWr{3#al1r-bT^4$p1_!0@^BK`>u2J8|j2NBrh3lazy68sI|59JvT+$QV@=Mm-(3Gf&X^aBj=@BbAO-w^{11sV1E<q6yj4+aPdFg^VI0tX)m@Dtt;`~wXW`vubO?+X+8-4X~3@ZIq54IBOn?%@&r{_qg~(f1bx;|2dD;rJHy9sD2r8}|t84Cxa56YKuU>gx9R^9}0?3;Xrt6Bh;h2p{+O3-0P102cxS{0jC5`S2C^`TYpp1TOIK1mPa>_U7~C`}no%75y6M_v8{L|K$+%_T%&<@C_0B^cEK0<oz2C-3;dy776m=>;gCh5&QHj1q=%g0uBT60uJ}(3F;0l5gOtO`u^+p^!yVT{09s3A_VsQ1N`?A6a^a#1{UM-=;ZR+`V}Y?C<^N7|KlPv`{?}%_2A<TEeRFx^7-Ef4F%gC^8Y6K1OfN?0}vMu2NMVP>-p{w9}4I9@c{V=0RIW?6XhiY5AqHH9SafR>h$&v=_dB~^Zf?>_R|Iy&K%+Y!WJzE8xZdB{V3KPGVBHm0TB@N`VtTE?HvvI_xb+_7Wdi^+~?^K6x|pY5BUlF@bwn~4D#j)_W=&w`UdUo-W${u1{W9r^8pA0_6Gpy2;}w>`UwpX@Dcz2DEtiu_U91=3h@6I1po*73G3?q`uQFx^b-p$0}BNa4-N0-1`**LDdFV@+4d3>CH4aj_!S(|4D<N;3l;_p1p62W8vzdc0@w2NDDA)S5Ch=b3-bo*=l<pi`YreN5BKNw0JH-6^dJ542j}bc?f)4N6#wG#6#E|g?gI1;FA@h60^0TF`T*$k>G9$Z)9nfH@A(nz4io|<^AZa94$LC^<|_Ev2lC<k2O{?xF7)ID@%Rq;;_Lzq{tMIkA`JEm3i1OB`s)WA7WNGI_z?>a00P<#6bI}W5%%*8?*04)2=4S8=<x3j5Cil1`tAV)2KE!|3jXl=8}$zP6czyg?Bx9+2J;K(9ttYk-|i~(2k$1__3jM)<roeR4*l;I68Q)G2<7td{Okn?6Y&rW`t%SB3F{631_J&95%K@~`rh^g3GEU20tf)}`Wy1@`5yQF`sw!N+U)r%=qvOF1nDX6{t4vl3h?vw%k1?e2MrMm-~Sc(BK#l;Di#ABBIp|s_Z;o;0{-a%=<fgj{sIyM3ia^uBn|Zd0_^z&{R0RI*ZnX93GMw95(NtA{r&O<3jqiT2ize3{`mPM_Y?y19QW$t',300163590)
install('tdq0x3',1600,1,'7V!!01`r46{Pyk|^b!c`0Ras7Q0W3E_6PR&?+gs-^%3nK1_u!Y_BP@b2n!SJ-QNur0~i+K;@>kA0{;6A`T7_M2lfI64C)d32LbN}ARpA?=l=la{reBs>;~}p@BZ=u<@G4}1}g{p0{;{z8w>^N9u*n|1Kbq>@#_Qu@ACNf7Wo0~{{i{=@9X^y1^NgI`vT_%7WEbLANu|h^#K|L>-q{4C?4ti1uN+82qF#$=KT5$@dNYu;r<2t-Q@%I=IRF53me=S4d@8%@#_N(=nMbw2-O_@=p6Xz>=zF1>ID1m79I5e><9hk0Pg1)`Uwmd`{?-=6$t$g7Y+dh3i$>I0O=h34fz!V0sIR4`3m+C73LlM^(zo4E${RV2nhH50^9jG^4I13{Ra01``+9nA^HOM5#b#D<JcnQ5e4}R-{%$x73;srAL9Z79q;+~6yWXv`w|ZQ6f_F(2oU}WDf0Fb|N9~5{SplaDG&tc91`jC_W1-52n7b=1oiF&^bHpl@c#n<0qq7D==%@?4D;^k8~gVI00#gK=kya8{0b8U6$SPK3jH7l2K)v1=<ne6IL+h#`1TI)0rm#o2Llcb7~}^95B~}Q`}P0_3HS*N3<?DX<pvA$9pNYD^#AG>AQ}hc_8<G)2kQ(R1N0l;5bo{l_xKh3-RtuF7Z(xfBijEFHw6IQ0PX|!_6_Iz2?p!*;`1Bz2<q(&2PY2!2O=8c?-3gQ=Fsj3B;NMx1^W924-)qw_woMb{_*MZ2;v9p{vIp%-X#3>=kDeO`xFTI3I7%3-3a~qF!&Y_?F{?<@FMB|3<=r!`SS$h&;JMa6ZHQM2l)FY_~_ma9~0{V1pn&y5#jFS;tUJp@&4=&0TBHI^zaAr`|R%9`q>`xCGrsb2IdU={`~Lr67DGs1?(B?5(EtL8|xke5ds1V0{#pK|MLyxC-vU%@EZX90}%cA4gl~E1sC=aBMIjP@GS)VBMKP|;`S37@A&%X2lEdS@f`#m=k^)>_4M}w_52VC{}lidA`8~<8vo)A3)c*9)$}(Y`PAz|@CWbr1OE&F5%BWs?C%O2`V0m8_#_S|{Ui1x^ZN`N<k00D;Png#6B^^w1S$6z<ND<f^XS|L1o8e2DgY4n9rg7K57Pzw+4>Y96YdTU^Y9V+8TkYa^ZoM#0|O2A^!E4vAR6ue6YB;W62uPr>i`w-0sajB?He5z6b1A8@aOsl|NRmY7y$+E7AG_F^$PR*_4V=`_X7mx1McPc{{8&%_4otx2I%<+_5TnD3gim^5%B*7_x=eJ-_GzS-}vwK{uA!z=>ORZ{}C4P@8tLJ`vC_9{PXVvDG>_w8S(}8{QLnL@#+=l3FG_o3K#hO?GFeC2Hy`G59Aaf=l}W$80Hxb1qb*H8x#Q$?%xav58V0*`x*ED@%P^uF7pla))C&x2mBfz4fP}b2<hn(<n-q;*6;)y<^U2B2Oa|)2PgFdCIImT-r*P_0q*_W79<wV`wrgv0QV^`_XYg<0{Q>z{ZaAm1sVS=-})vJ()aBQ9{KOx>i{$r4-)t__}%Ib{r3#-0Q3|C5DWGK?i30J`tk(*0{sgj0`vt490UUc=?U}w>iqaD1oY__`WDCoD+v4N2O19u3F75Q+7bT$3-$>n2?+}U<_QD+?gJ2d7Yi8i2QDW4`0etw;U)kl{tEQ^@e>!=?E(kl78d#L^b;8F8T<Gc>iqcj{QKqc3;Pf7_zCpz4>9x+8Ti@`(F5rN^)=u08zJ%wE#U$08ztg13FqYv5)kI$7&+5D^DYPA+65ElKK%y(77Ql!4D9v*?(_K%1P2c90`vv}1qKNH{sR69_Uilq^Y;kx3ij~u7V_r!1O@^A-UI#s1_~7G_Z1;54*>rH^#1zrCkF5a(F`L2<OSja*$vpuD*_G*)e7<ZANTy_0wx9!><upx9trvg5c&e_?cU-0_4dW_0}l!I3*HA4`sDF3{O}C(@(m^M2O<OR5bFg1@AWYb3itHz_Yn;3=mZq^>+}ov-2UDB05JOq79#}>{sHY0{QTs~5c1a&77!c26c_2y2hb7W5exw(',1000282982)
install('tdq0x4',1600,1,'^x@|Y`t|?_=GF5T9P#@E{SpEE2KNUO3i|XM693%v1rH7b3-|c-_#Ni`=iUSB*Anvl{|*q@{tp)s;0E99843yT{1hAm2^A+9{sizK|K;fq0Pz^+8}0@09Sa8g?Gfc32@??!;s@*r2K4j^2NMYd0VeST>;3!n_wEf3=@Ik;^aJhsAt3?V`{?!w@c0e|7W?S*5Ecys2oeeg{`JKbFVPP69SzC`_A2}P_~P~w67u;06A&Ea_xb$$)(H9J`0wu{6Y{M8`mYx16XNy}0y*#w)U)t39qr}~6T2Ji7Yyej^+fsz*Wu$90T<x`0~Idx_3jel#q}re0PEHn3K-W1^ZV2`3k1{f@(ud_@d@(+69(rg6Bq6R{sr<2_YDrw67~D=H1`xB4E*Qb4BY<A^ehYy9~2Z5`uHy!{;AXJ8vyzKFaFKu3;)OO6#M!V+~v*^_4MKm{pjua2mbQ&>H`w_-v9gs4FmMv03rSg76j=G`v2z^<NDng{_Nu_68Z)a?-A=D3kL4)1QrtgCKcfu8#37X>(=1;<nIRz00Qy}75Vcc^Ai5;1OfpN4(s{`1Sb*+2NE3){}1sg1P0yw^9ThA+6N#R_6Hl>{`Ktd7#0-{^BU<j^a2Ro(dh2o@*T?g{w4(x@Awks2kZ_LCHN%*1@Z$1{`v0r?dk3f`xO`Z3F_kO1|<#w{S@Q@@B{<`0mASE@!bOt-~AN-0SoXI0_qec1Op)q3;*#34+;qn78wmC=kPB8{q@cT0W1>o%M$nk_WkDk9p>8<3i1l#>J8!R`}_O|_W1zp0Q3<X(-`mS{tVyl6A1MN<nIy={p$J_|NI;Q1PL1R2?YiW0Qc|^{`vzU>=5lC6#exQ{|^!B5c=)xE)@3n>*x~d@EhLz<s9V(A0QUv@B7{v%>e=w^aJ_v{vPoA4jUN{90?-p3hB!$5Bu3T*#r9-E+xj`^z-!#1QZYP^zZTn4+QxB10U)MAL{f0(FEcd{PhX@4gTX50QK=2=p-a4`vvqA`|0lb3Ejoh{teh64glc!4)7Kl0{j>J86)-h68qon6BFIzHS-7h^ZO7(68i)Q@Zi?;8T<l1=JN&t`1I`#4)h%X?FRbZ4i5?{+~61q_#_GT`Uw6Q;{Wv!Aol<W>--@J2k!tL|1IJ7=>ymM57qk?;_(>~4(0w64d&<pBJ&pt5fBya{?_OY`5Er-4j~N$APDXO_w@Dh-5LV__wd>0`3vX(@CpAj>+=%)0Q%ea@c|F*<P-+`=mrG>E$G_^0OJA$GY9tL_1FI6EBgM@1`PWR=luF44EzA$5fB;_2@LxF1NjpJ4hR4F`}6@0{revl0|x#I80`e_0QU<25C#DG0s{607ZCj)64lus)Dj61_UhsT>k#7U82afi4e$x{2LKWp^7sf3Dia3|{QT_)^X?J^_V^9*6z%Z=6ao7F0u=!C<>M<25dYuf<qrG#^a>IU@aPl{AkF*%-|-pw_5J)F0P+nJ6Ak+a>k;?z;R6Zd1ONE^?;!vc@--Ou{2mYy;05{W4-)JV?Go_>-~sph0P+YT`?dk|+yffQBs%UACg9lv^zQuz0r?5?2j=<u6Zz%;1`rSY`tJDn4-E+i_~rr>DDLI$|M&s{66yKyB>(H;%Gm=1_A2oQ1PTcQ>G>BQ`1t20@%j!J6*}z===uEp>FNL`>h%Ku0Pp7s3JnVl?+o_&?hX+o^Ar#&3ik9S5e5kP0R{d4`V!jr8VT$g-|q7L2PFaa3kK>A0SWaC^Y{hr{@vyR016c)-t!3k6$l3R8XD3OI`$P5_|N$A4iCxF<_7@!>hla60p$@Q1``Jd>=gDB<m&$k^y?1Y2I>C-5cu`>1{eMK=Ijj&{`da`2=4C!009mG6Ak(85bEX>{{<Ba1M~Ct5E&EsAPWBj@d_0S`SS7|2KDz66%7CJ7xm@d7xEwp`t$z`72g&e5%?PgBJ$()2lw{|0Sg!c4Fc`_4fF*6{si&}?feP}^X=m0^wR?l4EyfX^Z@P=2=nm<_UIb(3HlTF^Zob?1`qoB_|FCr?GY3T_xR`i_yZ6Y2MFNz',4119665683)
store_list("tds1",[MODEL_ID])
print("Part 1 of 8 installed. Run tinydata2 next.")
