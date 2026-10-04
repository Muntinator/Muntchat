# CalcGPT 3 model installer 4 of 8. Run in order.
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

if installed(4):
 print("Part 4 of 8 already installed; skipping.")
 raise SystemExit
install('tdq5x3',1600,1,'^y~=&^bZCQ<`VY_1u_Hp2loC368H!G1@#IK_Y4mJ`}+F`3Kh`+>+%;N@H6uU2i^$?3fcJhCjS`m-T3<i2KD~`0Q~*-_5c0}^9}g<?)D7#`}hI}@D(Hp0s<QG4g%%q>gg;c9vS%J`}hs^2;~U^`~>*^^aA<)<^2pA0R;d0`SKU?@%9M)`|R`j2?F#2{R!Ri@A}vT=obwe{owrN8vyYF{t4^z`u_a>{SEdI?E(uC_6`CR0s0Q|0|f^GCFThX1S|pY`TFeW4KU{a?+5Sr0Q>k4^#$wx2^jbi0tN5;3i0{%1_SgA@Cy6({sQw1+zIIKA1&(x3FP_-{`V05_VW@B?C|*!F9-q$65k{u{u%xO2p0D90SVpN_xuFy5DozM9tbYz`}_0p2n_WU3KaDE`U&;-_vQKU77_;y@COzKIPCZf>eK`e<rNL`^a1bk;tKfU_4N)B3KIqS_5AxB?E(Y>5BvrH`Q;D?9q91>2PyLZ3jE#U5HSSs^ZW7-2LtZ&1>XSn9|G(X1<vUF`vD9P=^+j1>+}f*3I`Mp<N^T^94G<${Q30{@&F404D}oX00=S<8Q=8()$axD+aBW-3HTfM@ay>q5y}JlAusC`1QqQf><1nd6%hO#1m6T6=j`(Y843CaANU{)0r?00>Hq5q2>c8L`5gZa4G;JM`4J5b>=Fv}>iPcqHUt$0@c0fH|Lft}0RavC@(ck1>HO;r`Ue00_TTLG^Ahg~3;p=~83g3=0{#m4`2!3E;|2Kf?Benh>+%Wm4F3A$7w!f72I~b05eoVY1Pto?_5dFl{09RA`33&_{pbqw3JUS^_yy(p1_Ay1|Mmh1`2PXl5&kIg2o(tJ2<;9L{3G=G<oxft?C|N>1{3T3_x%hBD((XS=kE#}@dW(o=?Lx*@ACTP{{IsC`XB!45e*yj^Z@Ja4i@ei{^<%01Nq|;`{4Qa4iF_03ijsp7Yh*k@fG$55#<RW`}qs%;r93H|M2eS^&9yO>i7)$7U=^R<>C6~{s<5Z<@*Q*1rrAM00k8O{p1n!CgvOe;qd76*ZmC)6$1Su_5J)4)*=A_`UUOx>-!S%0R95t7V!W6`Su$F5c?4L1sC%N2>Tcv0R-&y`Re%+`0f4t5bhBi^#Jq+<LCnb{Qv&{3>N(O6#*3h`}Fnj^YQ@<5a<o~02vGt3F-z83Ig~R3kcly0q^|$|Lh3u{sIya9~KS=4gCcI{S5p21|j<S<@W^f0{jT;4(Is#_yQ6GAOHyX75n)b`TiOq4A&s_CH?{M_yzs@2@eJD5%K^P`w#o^0S5~P_!Jx^{R`#s4hHxc1P=cE@%sJ#@AnJ`_5KG082R=7_X+9t3km!O59tH$?E?4*2=yEH`v?9E{{sc;7%ux1>IV4l{1FH02=yrf@%Y*Z>H!7t0to*K2mSQ@5Z(|OBJlA85#R+T^b!031P=%8_x<DV{r?yNAtnYI>=XF-{s-|G1^)~G@a*>s<pK%{0{jF9^z!ot{P!RI5(EDB_yh9!1_~eH4gK~Q{tfu@2?GoC0v8Vt0N(=_5at5q=okp%022@V>f;;|2@&t)3iTV~`5XJ<?DF^f1Rez-4-5P73kDkX_y#Nb0Ot$v0Tuca9Qpmw@*U|3*A5HeEjhjy68Zbl?i<<z1PU}4*&*u?><8To`XTxx0`dss5&H%H`2+C%{Qn5}`uPSA{rLA1`wIjA_W2YJ{O=L?3H}8P3mNbP2>R9Q2^bjjBl!XW0q^w+2mST!{{0jf0u2-5?hOVQ_8brQ{Q2q`68rP>@%!}G{umMbB?SNr>hSvi1os-*?fnJt^BV~P4DRd&1nv3#2pseW1q12=4(I#=5A*Z_-VV_9`2Fnm10L`Z;qU|y_zdz11Ooc+7w`1?03z1%0q*|*673E0`tt-85Bwnp1_TlD?GF?A5h?cV6aEkE{tw~y6x#9d3+V;^2o>`S|Mw3D{R9yU{r3nH)b|JO1q}NA<Ocfg`U~O+00r|9^$rgN{1yxA0q@oY00Rjc{0|-E0p0-#5%Tr_6z&ED68jPn0}2Hd0v7Er04y2V',78062748)
install('tdq5x4',1600,1,'`T7Fl=K<yb6cXAG(I*7`IpY%s@Fn~9)cyk>{|E8)`~n;U1_%TJ;Rp5x2m$B`1qSE)5cm1|1m6(x2Kx^276BUz01W^J_Z9%`0v!?i{reCE2n7x32=@>34*v!P5da4e2?GN7{`Vpk`whwk`12R-^e4~>`xnAN@&X4490~CX=iChn81^09CF=m)9`x%f>EsXQBqS94`2Ga$<QoI)2^0C#<>m(Q>-^^)3=a(c4haAM3HbK-{NnfY`0D`$<r@&^G#m9S{qXra?-=_3E9vhL0p{cV`{mg12;>gn`r8)n_znC9`XuJ|DdG?A`zZka`tt<j2nh)M?;axk_x$<@2KDp><^uQe>IDb&3JC`U@)Q;M1P}xC3HT5D2KfN}0RHs&{Qmy(^8xq@`R@kv0}K8R`W6Q1?ei1-?Ewwn2=xj0_u~cr6cY;u2mJ;K0R0gi5C7xv2L2EO0VCz!`TOu91p5W`7z+Ra5BdQL1OyY&|Na6f_yPmx@ec^s`UwjC`SS=9{|Ey7`TQN+@e}OjA;~B1*&FE8=JW{@F6SNi-wf_0^Di9a6w>w)%lPg62lw&~-rf!j$RpnP`t&6C%l!E80sI--_UhmW3;^@`>JZrn`s*1j0`ULr{saI64EYNB0T%QJ7V`fA{q_79`|||&3*!s*0R{2*@cjz_3mo$X2J{N>?EeJ#5fk(e<KPel4Kx1-;Sk{e1nmX~5d`xH-17SS*ZScS008js_YM^R0{-?24ekLE0Q~g{^b+tE=;ZeD`w0~c`3&;#5B}}r{R-~=`Tzp^1or_89Ni@T1Ow^_79;iJ0Q(056A1kO0`~j)3;!Vf1okK2H~9ko@)iyq|LyVb1q2rk@(KF>{165G7ziEu=>-P`1`GoA0t5^H0{!L%{r%SN_7?aA4+ZxA4b=Pm1QY!84D|ji`}h+k5EB^t4-5bU@dpk3A?W@M-TVM4`~>wA5he%c+93G;0qF?@1P%w=5&}Ha2?Ng-0TdP!_Z_$Z{0!1P_4@tv5*F?a_2>)x7xxqLA^0rw^8oe)1Sk6#`u+d=2^0YE{_^_i6a@Yt10L4sAoLIa3Frag3mXaW5hMl+3IP5D`WQa;CH4gq5AX~2{srmh2>$T_3G@XE9}4ga>HG;D2pba(0?W_?{`u<!1oGeZ^%MjU6#ohZ`~w65821wT8}0TO`1dyY1PSos673ib{qX-sB?AEV2OIPt@Ch*X2?G`e8}j=I-{}Mr>=PRU`Tq9)^$GU_1pE#H8VvpZ-sKYI5DfPD^aT0_0U;3e4*>@Q2om}R4f7Er2q*^j1r`?j^AYV0^!WZ79Ub%i_y!0Z_Z9{9{Pg=C68r=N6YS$C2<`*w_ZuPc`1Kd_@e~T_1P<#C1qcQPGy(ey{p}SV>H6#p?G)+?0q*Da_wEl2*Ax8t{^}d`_5j`Y{Py__4EF^V91Z39{{{UM2MPrl{mvuv9RUFL{}TZq<@5RQ4)z272m=N50`U|43lszi&o%b?{_W8e3KHuHE<+Ls7ys_~^7;e~67vixBl7D82L0sz|MlGp?Dr2q_xb_(7W?%Q{r&&&{TL4i6#V}N4gSm>1^EW;BP#*`0L=db<^&h^=KlB;>loY>4+i<(^9=<V=hzoB>-zWr`1<w#_v;Vx;X3#8^Y`xk0R9US?g|a+1Lyqu2?Fd15d!`M2>t&M{1FKI`U~g=3h?;;{tWEe`vVRR@B;7?^$P$4<LMFy+y(mC5B|#x-UJvO+9~Jy=n@q9zX$H>1NasG@CEY_^aAPl{3Hw*1?L3x6!-x02?^%(`2-IF@csY~?)m%`3k2v2=mPZ-790Nr?)vi)@Bjq`3-AXD3n3Eu1n>*;?+fhs_2v~J5CZl43<UZd6YKm55Ag-;2Kg=g{|Wo}2owbl_zC&@<PrGo`}p+C3=Z)F0}tf`1^)p4@C@Sq@c<t!{s;yA{Q&^}5e^LU6bA(c_yqVP^$7$X`yc`E-6P}x8v6JI{xJ^b4FxaK84B?g@d4-i`V9dQ{PXST3HtT=3JvW2_z4IA_!ImNA_XV-@*Mx);qVL>`~Um_1{?Y1',1222119258)
install('tdq5x5',1600,1,'`{DKX4;uOz`u5rT6ZQ%a0Pq3X6#WGh1`QGd4+H)34hi}I03-AL1@8zA2>%WN<pBHg1rHAt_5cD03KIPX1Na#0?gsPv?*0Y${s{gQ{RZ#({rdX@^%3_3`v492`0xG>6$ADR4f*>f>*xaO4DA>I?g;+z0Rag05eoVV4(JXI^brgL_uKyI2@~_=?*-=g`~L6@_67{_`0@nz<qh5D{QmSH4F>of?fnJ<`1$q${1gK3A^H9E{|p5K4gd`K`u8CE5#$Ty<{K3I<@yZ}@e=w69~SlN77HH?0r>m_`S|(=4(I#)?-uR*`2r5{3-SjP2L>wm82SSJ@)qwC^!@to1MmqA0tEx^`~v|23=SF&1Ns^E1_cP`3+?y)=I-<p`~e903lR4a0sa{n{O$_m2L|o|_Y(>4B-aoL3<vG~0|EmD{S^WU^Azs~==u!%`~wQz59<XB`}Xzu3k?1O{|Nj90Ra;l3IP-g@7xjm`YQ_-`1=g^2Ke9Y<^=W^-wG1;>+AplBlgoA<N50y`2pzX0saye`w#{8^TzVz2=4mq4e$8r{1fpC5bgB(90c(B1_lxV_81Bh<^}=y?$+`Q<^2Wt?*JL$5ceAH{PgJt8TbU}4FdcD{u3T0{^Sb`2O9hj0WB93>In4|0}BlI;{5C@`VI#GFU1P(?)Cuv2l@R3<M-_J01yia{_yt(2@4Gf1qTxK@Cf)86cGa>5eC)p;pF)z-~Ht97xC%>*X#BPAO{=s^8Nh@3<2&1;`aLk<pKr(2o?YP;v^Rb1_lu05Bm7;@dfk=`1$hm4fXZs5(p9*2^-%S3<(4I@aF&m@%sw?4gv<|9P|eI`|t+&6#DrQ3;zV@1^Xxn2oU)40QwRH0uby2`3C_o2Kf;0{|f^8BlH6K5B?es1mN)f^Z)%7{uvVq0PYX^4FmuV8w~OL3;FvG{u%fB3=jSc5(MNH_5BPS0tor-1q$^20`&s)8V>vk+57|d1OEi`^Y#Sw3=sVWE&&Sl0|5N=0sJ5#_7mLk>J0h=2>0Lh2krL(@&G0j`4svI4EqZB2L$*I&j<tkA@}ek*7f%o&ocP?{p=h7_z(Bm3j`eZ75D)TANBX}^V<R$><sks*%R^m<nRjf0S*`ZAt46r3hV3v?fLx}^cVyN3GwXo1q${3{09y73;GET2p-QB0Uq@p>m?8o|K#i@3Jde(0`J#E{rMI9L(3cr58m$@858>R^ArEc=^gzD?DPxq$LRd>3k?hw|LyYo`4;&I4EF2%3<vh{5d07W10Mbw@&X3_^yUW_*Zmgx2L%1{4e|#E`1u9(76}3X_X+{`1N8_a{{js33ibN%_A?d(66Em{8~yG24GjVr3i<{B`UeCO0Pgbv;t2gM^%o2C5atmC?Fsh_0t4#>68QEH01w~z9_kVU{`&^#{|5dB0{8|I4F(AY_Vfh#79j`%5$N*<1pWvL`1S|^==lNs3kL-e1QrDX4g&c31Q6Z(5cmH46W;>i5C!|^`~(N|1Ns8~0TKoC799ie4C)#2_XY<U0}=w+@8$mK_7e#U3<Ce|{Q(06CIk2Q5f1<fAodZ=5c&xQ-2fQu#p3%O0t5>QBm)!??g0D<4F>=96a^CU{}1;F^!eZR`}_C+4gmW66WS%`FZLE55)k_S1L^|s0Pg+@{2}ZT0}=V}69x_b?e+`+2JZv$4)6a72lxZ_{Q?9E@el(23;QD#2M_BE1ndU}1N_|Y@A()Z_yPRj3jhHF6#W1I5+eZ(6$dHt0}<`(3K;tv0R`>)`u*(;_wD}X3jhlQ_8AJ==mXUg2oDSMCCd)=12y#n_SXpM_7(~c?I#WA9}Dvo2Mzn%2losC{_*qp;qVC-`2y+@4DR*v{R1KV1qU1f@&4lV0}1!r1Puim0s-d}2?_@O;Pxcu)bs-O6$t<I{_76<{ss2-AP4aE^$740{`L_i`wSBg@)HdP`0Dcb2@dz>>I>}l`vCF+`3?&G`1A|;5(PH*^bYy*8VdIW0}b&1<qiG#`TPRp6aC-`0T3Pc4)*;4009g31o8y!_U``w`w<8S{r&wA1qb=|',1227027707)
install('tdq5x6',1600,1,'+Xwpg|N9IK?Edfm{3PuL{`mq21@RB`8}lM2`R+0901y%a_Ydpf2ks0h75V=93Iq8D4DJsR1Nim`9S1i0>InV(7X|MN0S*BL=>q`t{OJ186c6kB1^)mC@%H};``-ri783RC^9twh3kLrE01X87{Qm>_7Vi5G_x%U_{{#*d{Q~(7|L_j;1PuiS5C`-N84f1^?D_r`_#Ns1^Uv_-1N!tI{{+_;><$D21Lp+y;{^@w{1F5i_Qe6#1{(qW+xZm%2oVD62?iVj5#`+c3I_)N_6OJm0QVOd6!Qq^00a930}KrL3<>)J_6X<L8qWGU74PQ~5d7&2`_T>XAn6Aj>njfP3;+%f_uU8A3^ES@1RWI%?*abd4(uWI0vz@R2<agd4iWm-1KI#E3H;<13J2=$3F-_4A@LOm`LhM{=>z}?_RRm+3^fY^^A`;P><SFx2<0Z{=?V@X4C49o?ez8>^&R~68xR086;{s-1pw>x&p7P_6YwA95fk3S^5y0p1_KJ#FahlE;R5Fr*u)YI2j&tbBLxNe5BKZt;s^T+3HR~<^#mCS;RyWN@e%IW0u}NP5&iA^^b+&}5D4)R5f%vl{QwQ;`w{~p000O30_O!5<PY!P4E^-}56%Vd^8Fj^<@yB!`~Cp<5)}LQ`Vaj12>AB@_2wJu2=EZ;@Ad@+^8xG(1RehZ5*!5P808EX0tEdX@A3cX0T31U^Z*VL3mXpj5&sY0_7ngq4jlIR`aBZ^0tEmY_6!d40r=oX2Lu}eF5DFf>I&27`~&<g3-<OE{2ccM5&sGl3K9tF`}_$D{n8Qu;r{~t+7=TB`tckHAqwE!{p$7_2G$A;?j-vi3j`_U00iXS7Z~Fh{uA~E@%{4)_xJkr5eWVc`vnvDA_m;_`xXKo_vRJs1NQ?C^9c_B3il2M1r_)T-tz|b{s9N-4(|u@0{|NW6!!xE3<CTS0s$Tj3-k;CApZ*R;tLe!1NIUJ8{qH$`TzC*6!i-E0Q3M0>HY5t1^@5#-tY7W=>r4(2o(7O^&JEF1PBB80S*BJ6afAK_x%a(^8pR@1^f&E{RaIN4*LuKB^Un&;QIXf0Q&R+{R0mC6Dkh;3j+cJ0{Z#~4)F~k`x6ir;|lu+{onNg2nhY`<_h)n`vC{|{`U^>`u76;3IY!Y{14ak8|?e{2j&G7E(Yc5`T6e)1^@vJ{SN=!;sON+0uT8T4)_7$|N9OD?*$tF@B9?={|^Qk*7O4J4FnSE{^kVy0TTcA0s8+24fhE5{sasq4+tvp^BxQq*9!yY@Z1Iz82Iw|_VD-v{MrEs@CEw`5bZJr>hS#*2pSOi_UP&V3J3QF0qzI=1_}Nm{1EE~Iso_Z<n#s=_4xkq_xt?)^zH}l0rnFH1{n$m4E`SN{QvIv79R2Y0QKew`Uvm=0OJ1u5&Z)o0_yMn2nY`m_w4rT^X~=?{Ocz8`~C<A2j&9oHwyLp{RHI?(IEjg4Gt6F-|y-h4GjMc+UWrT0SMy(`3)cW1?CR(;1>zm74`uh6zA{z6#@7W7UmKD=<oLd*ca^7`Wx^35BTf`-v1pN@AU!r_xSh){s0K+{s06L9|P_M4CNRK`4am8;1~_^><1S51?~h14G90(0`dg++U@4?@Hg=e^854n{}})d{_NQI{00*d{uKoK5%L8G^x+xb{PhXw694rR00#aC_Y4UJ4+;tN!4cjDwC~#L{`c$<!6(lG`2HsO*8B3v_!K-i7T@{?@&gAA-V^f?@fI651_2V_^cMX14h0zJ2M+fT0|x3L{sR{0^Y{$t2Hpb>1^WFA^B)8U687)y5EJk7A^ZUT1L+_58u=3R{ty=c00RLH`v42}3m*ax6b<tk2nqS<^6du-{p9Zk=mGc&1P1s267}=-3H2oX3i<E-8V&^Z0R##55ElXc^5Xad1?mU|>G%QQ0q+R<4*={5_U;Dh79J$^_yG?E^A`;E2L}7^{R#Q+3JCQ88Sm@}2L=4<4*?4W{Q?08{{jmM0Q>_G=;sv#1`_8S+5rIX3l{A22mSH{2=WR51n&+8_X7eA3<viI;rJW(',3200379138)
install('tdq5x7',1600,1,'@9+NK=_D}^>c;W{>L3OS4HW|S0s;yW2mtj4+5{Nd5f=^p4*BU25CaDJ3k)9C_Z#E=2m}TW-4NIe_!A)$1pWZ~4h`w=`}Yv{9_|7L3=Q%W3IO})@c#$?`{w8n@c8%s^9b|<3HR#v1NHp!_W%L;0uAW_00I3W0TvDO5&{VN6aNJP7Yzyo*8~*#^!Wqh1LFk<{p}3~4fqTJ4gLTX5B3oq2m}c%Fb4Sd*9{Kj-s=A74g~ra?*ZB9_yYavA{P4G5$pE*3IhW)1L`p14*e1Y_VD);0tfX32J!m{`xo&N2LuHQ`uh3n{{RXa1OOfS^$7F&3<L}LAu|9i?fe4z{RHs})&Tec9vS)p^3^B!0sRR03+@^X`1=9z(+u|Z0~`zo7To;U?+PIK=mY`f2?7-U7#sZs+X4ji_yGLn_w)_;5B%==0}b;64gdi71pgEx^$7R)3J3iP3;Oux0R0R21Ofa1{P+k64i69R1|$O>H~SGD5E<VJ?$zn&2q7B%?Ed-;`xNZ$0r>&~3OWb>5$y5%*6jQE-_!;H2k!~K`2Nxu^BnU3DDCAK{0sE{<O2d53>N>~|Nj*G`}p(<?)?4`1_$&23=9?d7yat_5A5{z0Sy7?`uzVB0ulr9?EVNH^&t-T4ekH_@cjuJ>h%Zr82bYJ`vv|M`~vs{3IGTH^a{uT2j&(1`TgwU1p*H#4hkCH7w-574gn1W3M=^(9ry(d|MU4G<oo9577!H)^a}X$1NZm#2k#2t2H_F)0R{aF1Mk`f`SK4e0{|Ec1^)jH_ZS864(|8+E%Oih3K-oX3F!db8yp|_<Mayt?j7>w{|Ef^_!8_B=;{jl?-%_I0}AZz`~?02|NjLG|N9#S^7H`+?EC}`2MGfQ@D%p$2P*Ug0{8(6?+g0*1^NjD{|_1i82<wb1O5IC=J4|M4G0bI2=xKq0LUEq`S1!0-1Q9f1^@Zx`sWY+92Nuo0|4(5{tpNM0s<Hh^bX<y{}BNT>kZQV`v%?m0Qm?J1M&GB1oI3A`~D0C{rLtF1On;^<o^Ww>;MV-2^0YZ<s=;S3kU<_`1uhL{0H#=>i+-=_XY&v?hNb+_6Yw7{sjOC2n7k~=L7Wn)dBSW1qBTT2mT8DE)(hZ4G-q_5BKNk11#|Z?idF6?Ecm9_y+a*`v3q9{R{3C3<nDX`tu10;0)v63jNj&<rfVW-Y47h5AqKT)bS7M1o$Ea_WAh%4*w1d0S@c>6Y~)#<^%Nv6#fDS5AXp55(f$L(FX|e=LGlb1>zU`@ap^h84LsO1O62d4Eh%(1Ni;_7w!oL2=wUv>G=^76$keJ2K)*W1^^J}6a@4R;0Wad`10ud1p)T=3kC=V`|$Vx^Aqmv5Dwl40wVwb1QZGP2kGw+`}++k2owtH4*v8Q@dX9|7V!WT>hJOY=k@<2`wQy$>O1uo82R_-0s#IG5Ag>Z{{su&{`mz5^DhtZBi#fRA@&LI2nG%W1q2KT>=gV99@zr!-s$@lBIw-h2@l^D`urs8>;eJ52K-J369n@2^$`OC|M%kS>;Lfq1pWpH`U~_I1ONyH0PqI@;0Em#@Bs5M0|)-x?ClTz^Z4}=0`Bqs5c=l+0SPJI^A!FY^abqo0M!N&{uB`f6AuLg_tyvz{OaWp7uX~G0r~729}^7I+U5EK6bJqw_WSV*2n8DaC?Mkj{0sO7`Tybp^cET__6qj`_y+U$`|%6$5CsSf4EhT53itUD?eGQf1tlK|`3MvI`yLMQ1_ci9{Pg+|0t^ra1`pcr@!$>!2K4yg0Sp5F1Ni&;3=RtT_3{WB0Ri+O3n2pT+9m4x3;+NH=okn21N9>K85#Ec3jPuS4+7o`?Dz;J_X!E>`TPR{0{8>)3KRbL6Z8ED_xAY(@e}z81Lpn(3la1U`~n634HWzj4FCua-~tZ)<r4x74Ep}~@do_@0R!{`1{ntW{r?&9;@tZ9009g6?fe!M3mgXw3=jt({38Sy6aD-73K0Y65B3ZV_2~uw2le;v5BM4l3l9ei1ONy491;)x1myzu0|V_7=mPox6CVHl2?g#2',3345670726)
store_list("tds4",[MODEL_ID])
print("Part 4 of 8 installed. Run tinydata5 next.")
