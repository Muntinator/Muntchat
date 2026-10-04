# CalcGPT 3 model installer 3 of 8. Run in order.
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

if installed(3):
 print("Part 3 of 8 already installed; skipping.")
 raise SystemExit
install('tdq2x0',1600,1,'=kDwJ?)UiT7W6Rw0tWE}2=4_BDD3kC8Uyh09ufxo0tfpG4f6Q@6#D%F^aTd|08;}1{R0H{`~nX6-0kQ2_VNM&{_OV;^Y$P9?Az%F^b`N>^a=C~5f}&b1p)v6^Xv5g`~>jv2nzxd3jP1`0Qd<G7X$I)91H*t0tE9N_zvm(2OIwm`}hD275e++4*LB92OIVX5ApU1`tJh;1O*BX@DTtT0Pg7~@CEw~5&jbH`VIyU00A2J4et=}0`Kh(_udH&^Y;Jq0R89-1sU-J<NoLe@#YT}1^(sv=m8S|4-@|K2GaBU_y-3W<pJ&T0Rs2?666Ew_W=w7`|Jz^1N-#Z0{Qq40P*hy4H^FT^8)nn{O<t?>Iwn)`R4%v{`wC12>b>u5(NMK4*=f@1@ztL`~DaP@dO1K><I(>`2HIX@+0p78wLFI2Ilkr1{wbs{sH{*`~mm-0sIOG`urRF3itf+5C7o)3-<{9`49X9(gzb1`RxD%3H<{B2KxvI8w3Ce`v(sK4($gE@B9D(`ug|z|NQv=_y-ga_WTzK><j+u`SK6y_UIJ>>HGrg`3(gL2@3EY037QI5Bdl900s9F{QLM2{O$k!0vq!J^$ZU81@s071_=HP_X7A1@9XjN4+;ba3j7EV_XG<Z{^<Mx2Nf3)5(4h{{TKfN_W1@65a{OT{0aR0|MU<9@dp<n`v(&X6b1<L0{8j?77PXQBJS}I{uKWC8Sw!H0uKE90{{g6{{#a91_1v3|NQ#;{!Re~{{{U2|Na601_j~+`1uGN_Xha@6%zdf4)OpS1O5r-_xKeF3g-9q`~3Cv_x||)76S(y@%|(4`2zIx3JCE02ml}X@BIk>1p)mE^8y45{TTcH2?+lJ1PuJ|2=fW}5cd)N1_KK60Sxv1;pY3&5fBUN?+gS80`~*}_4Wl99}p1r5B~T2?)w1)74qQ#5dZoM0_Xz$00;mH0u}ZQ`|l0=_Z9l<`u7L)3H##u`vL#|`xpEBAqx692LuiO{1o#C4)O^E68z)*3jFj0`}Pd_3;_5g0sZ>-`~2_v1M&F-4+HcE?*;z%6Z`ED1nUa@0{ar-4FCQK{Q~kG{S5K@0TciL`u+(S7WMh~5%mTC2^#|l2mkc`0{#F5{{#mI1OyEC|Ns8~0rdg{1p)*d6#W7H{P+I*00Hp+@&OV90rUY00Rsu^_5BF?{|*xKAol0{{uT-d^y}^M2lNpa_6!H+_yzC!^86zB1oIXI<OcT<?K1iz0Wb^g{tf#I`5ET>8Uzae?<@Wr0^<D%_Y3#<`Thz46AKCT2L<>5|NZ?52L$*y<K-j;?Cbjw84Uys?cxOo`tbSq*7E%d0{{H;E>->T|M}?*11KKU9Q(=o{Ppzh0q6uD@)HR2<_q)e1|}Z&-uDv?_ZQXg1n(0W5d!iu4(Ztq5cVnR^acR{6an@0_X7a=@B;+~2LA*01O@*H?-K(42Ko2;2mJsM`yd1Z`tJt$2>=2c;?Df~{002?{sJZm5(NbN`U3O{=>HrP{to*70`nd45)S_j2L=K9+!Q1i1@HeA?FtMA2Lb%}1nw9d3+C?v`S1h^?(qa14Ltb=_Vo+}4E^x;_5=nA5epLj2mA070tpcI_4oMs_Wcq74*&H6@dNtz_XGI`_WTbK_5t+({{Rg76fN`N|NH0r0QnR9_Ywf)5cc>C_4Eqz`U~^?7#tG>1MlPk1@H13`ReTW5cTy87X|?g0}S{a2mcHU{}uc9?*a7%`zH<63it^S>i`Gs1M3Y4@(1!07V+Tx=OhUX@aX>k{s;Qt`3d_JKj`!I2>1xv0t@>62lyEO_z&sc2mluq5CZ577Y`Et4<gq!?GXd~84?U10R0r^2LS!~0{#X44;k<7@dfw|@b>@*{|5&N9U}q$0ssg11p@;90Rsd81NZs@0f7qx2?q26|NQs|4(k#M1pN>t7xU}_{}&1g7V+>K2n7HK3;OT#1|R<m{uuuP4FdcM_wxVf|Na;B_W=~g0Ppto7ZCmF>-8K8@(Bh01q1m2`33R|0Q3>~5$*B|0Rsd50xJv&4-fkj_U-Wd',1596590293)
install('tdq2x1',1100,1,'{txd9^#T_B6ABI3|K;%W760J<<{lC52=?|b4Il3WE({0(1Pk>83LyR)<@?b90~P`R0qx%H=N9$-${rZ?8usi53>)(#{Rac6^APY^_#6QS)c)`b4FTQ(0qF$$4)Wy!-46c|1_=%n2^;tK4GjJT`V#aH3icKq5DNS72nq!l;R6-=76Ann?ffV44D#X@-w5Lz3=9S9_xSl1{Wbg@_X+<A_89>M0{s;C`Tzv){1XHV0tW^G>n;cc=?MVz0`K!D7uVke_WA_@1_ToG2mcEW?-bkn`11ev;|B%q0MhmW_vZuX{UaD9=^hyZ9r)@L4gBm30RH_b`up<!3J~ZAA{_SQ`}H9v1o+zq^8pM0{O<Jp3Hs{)BjpAX3<?qZ5dI7W4gvlF0}K5L6ao7L3L6ar?(Pfm>jM4;2KDs!0`L6+1MmR+0|)x|0s#gF2M7fV_ZS591osIH{U`7B>h=N;0|fEx68!@M2Ko9A1_uTj4*%f~2M!Af`Rf=B5Cj7G^cLp+82k|Y=<fm+_5$(f6bAhK1`7TI{QB|o4gmxR_WuA0@cH=x4FLEj_8kTY_x%z84+Z!Q?)?M`0{H&{{n`-c^%&mr=@Iw?_Ujn}<OcLK2p0JQ9rphH3H%rU77Ppz|M%PE81@1D0s#B|3kdP?3i}oi10DJm?hpDA8ut?f4E_8Q>GuKt0P6xK?j!>-`2pwq4E6>N1Mm?974PZy3i<{R;S3b%=kx~j8UzUZ3=Hi53<w1M$p7~K0O|({01NyJ^brOa4F>@h^7a)6^au9?0Rj*B`St+-{SpZO@9+}*5fc6d1MmXz6bAGD3HkX41N<2W7ajH)1^E62`}6n!^6LQr{TK}N3gq+y?+63{3;-1X{ss{C{`>L;{PF()|NHRx9S#Ho0QLt92=M(31_I?I`2`;OD)#j+?G+^M0R9j46)qGA85;fZ688u#`T*w)=kg2i?g$Lz_xkAg>kb<H{q_C?`U>p$-v0yu{{aN{2mb*5{RIgE1n~U{2Q&`-5C!T6{rvO`8si7~2m=Y;1qu=h0{ig&`V|=e2KfXC>kbM2|NaN|@&Wzy0qOnI{`c|T_4O75^X&Tv69EMH`3Vjv_Y3v_5BTi$^$iCB2kr**@%;u01`Ze_`4IN+0toH_`UU>}|LX+?84CRZ_xuA10QLkD`5^rb2?7NX2mJf$_44fj{1XEL4;T3U4Fmt`1N-_H{|Ep51?m0%3G)sJ{rmYB{r(&g68Puw3KIbn0TKQX@&W%78t&@-1sB*V@#Xjn<Pr1&|MeLM{s0E>2mBBO`Un}=`RMur0oCN$9_;Yj<ozM{3l;?z^#%p?_wot@*X{QG>h$XY@$m2n3@QBx0Q>VA`1AD;2>1g3|ML{??*kkA@hSTI==<;83jf#u5&QlB4JiWs{}J&D',3064006248)
install('tdq3x0',90,1,'==CE7DHR|32k;>D{u1;c{SYPy4FnhlIw}ekC==Dh?a;=Tx8dKnyvo_R&Bfry*z45D!R>()%gn^p6cGLW0PQUn`Uw3F1n~s#1065%5bzNhzv1rg>m~pI',3996790513)
install('tdq4x0',90,1,'?(--FE)X641M?m90S@^i0uLz-6AByxJueIpG7{Ch@YTkcwc+BnzRK3K&&%J-&+W^?zwm+<#?Qam2PUpLQQUeJMJtstHmVG;%YRnKQrT2Qt#8zqiBSLm',1287334918)
install('tdq5x0',1600,1,'_4O9&*c{Xf^zIq#-w@&?4%_Ay;0)X5KkE?(C)5Y>2m=K91^4y;0P+(V2<QO_2KosC6#U2l4G8cS_w^R(*d5af^XnMv;1K314cz7!;RxC0K<W<%Ce!oW{QU{~5BLW9`tS<*`sw%s2!9CX4hPNf3i9;l_x2a+)*aFb^6ePx-Vfp?3)<xu-V560Kk5<&DbV)y7wOm<(h2kJ80_B=<tGf?<`~}#+~z#$4+bdI`Sca))f><V_3jty;1S{{4Bq7y-3r*`KI#w#CDQo!7V6j<(FybI7wX^-<0lK-=NI4!+~z&!5eO#J`1Tj-*BR3a^z9h!;SuI04BhA#-wNC3Jn9b!Db@M*7U<L+&<OMF80y^-<0K8;=M>!v+2%s&5(XyG_x2X()Ev_X^6wex-Vov>4czAy-wM{`LFf_(CeZo#73|g>(+KnI7wg{;<|z%_=NI1!+~+>(5eF#M_w^U-*c;Oc_3atz;1J{}3ft!w-V561Jn9bzC)M}%7wg&@(h2nK73|><<R=T=<r&`#-R3*!4+kjJ`Sld)*c;Lb^z9h!;t}L13f|@z-wD~~LFW(!Ce!xz6zJF-&<FDD8tvZ_<s}T-=NH@z+2uXx5(g#K_w^X-)*jFb^6eSv-VWm?3fkut-w4{~LFf<&Cerx=?>O%VDa#KACFu6=;r$Kh>iP=<_VNGt;_m4?2o&QV6$b&?{rMjS{pQsI{Qdg#73Tx<?)~Hm2@?49@dxq(8t?G&4;}RN8T=3p4+RJn^#$zu<>B}fA};Rq`vLS4{4wd`^z;)T3<n7U9qjB7`TFPT^9&32_5lR`3H<c=68QS_BKr{+ApPYOA^iIX?&<#x3I*p8=mH+y`}YV4=HUVT91Z{h3J~xe1^m?F3J(1aGztv@4E_%r4FvrW=K=Bl`}FYQ6XF5=+XdqW`V<@h2mu4<7TN0w2<rj@2ny%;0Qm(6>-z>5`R(!t5&#tg4(1!|2@eGW^7tVC{Pz;_2;lPf6dLE!2MP4}_WBeQASLGs^%MO2_5lP13jpyB_X_(3{`e36>lOD78}<eH3k~e@3=0GY`S2M3@e=;~*W?o=B`o+X`5z1<=KBK}*BSm32mBcPDevP7_4W(w00su`<ow|Q6#5tM5hn!p5Df(b^Y{M^`Vj^J)AIc8{|oF7>-P^R4H*6Z^yUKi`2_s{3-SZ}{P_F{{Ravo?d}ux4=Do&|MmCp6b0=3ApHRQ0R0O12K4Ia_7*Ay1p^h|7&j9h^$7I#4e<f|<>LhW1^OcY=<o9M><Q}tAn^J785`^E8VDQ=4*vcW_5%O%;^6xh0SzSd0}J@$5ikH15&QA@0QKbw|M&;>@%Io0>hSj*1_k62F&Pd7A`SZh2=_zs?e!Hz0`dF(;Nu+}1`zZh4-f;?`S=?M`R>*M_xAS!7wZH5`0wrk`XcoA_7435754A;5e)g}7WE4X2l@yc_yz_G+w2Mt{QKYr@dgy}`u__Q==cW%5)lUY0}l8O{`KPB3l#MP`~3g$1nb%e69@ei<^%Wh<n0Fk_!SL5^8yvv85b4#8vWo25ZvC{2<Q>x?h*p==kNgl^zsE2>D>VK-TvwY4FVbR5+wuk4iO6f?gs!7_!|uR((m@?4+7-}77Yjl5ew<`>-p_0@%{t-1poRA{~q@e2;1Kl9s&^p1=S0+?GN(--0dG1@$L2r;`9Ot{1o#8`4sC1>H7vH2M-Yg_wy0`{|yrT1oHv!1pM#;{TCM={sa{L`7-+V1`hl7FeCNcA^8ym>HzBV@a**JEA8b12?7WV76JzR@#_=k^Y#}1^Y#x11PS~91@ICK=?Mo30O#`q5)1v~>j>`n`uqy~0s{m9^!Wnv;wSF@2J-?n4;uI6?dtmq>FEUe5f%Od2l(a;0R`{`0sa~L3J(9<4chzv5ANa!@bm!)4*&oJ-SPa~4*@6c69g9SB@+n_6&>*D_0$Cc`|b|i8V2q74k8o=@ed9Q0^#@g7Y+2}>;LEb{sRC4_!R;4?d=En8u0`9|M>Lt+4~9p_6Ga<3n%*X<oXK{{x;<H8QBd33g!v~+w&vL',2287547321)
install('tdq5x1',1600,1,'-U0&W2>=KM;{5yq74`G{7Z&y5Fb?qw2>lZP=I8<l57Ge)0v`?Y5%CNMCl3A=5b6v5@*2_w5%l~R0QmOd_4eEa@&^b4`Vai<@BIlOAmji80}lHP_UH)Q5*icf`V{-=`v?c{^b+>(^WO&?EBglr=<5&{=o$k6;sy8n;r{gM`|Rxi`VZ&$6Zjz52^8q?9OvH*3;`7oBM8?63>*g)2Lu2K_YC(H^zZ=k05tp{4gCS){PExF`ugz>{0;#D_y+U;0}>_j0tw^m3<C5T0Se*m`up(s_2?Po@c;!3=i(Ob7W@VK4FdZ801E`=3i<>f1o{K`0SogA0u>DC<ofah+7<vQ0VWp*?dSai_6`E~1pxUB?*8Wz1ppTl9ry46?dK2=_x=I)@&)@A0Q>>(5+DWq86Eb~1Ozhu4EoUb6BXnP`~ms)>h}Ei^Wg~N0R-v{@CPyY7V!l6{}lxG2>2TP3hn<C@bdTv3;OaQ0S*M@<@XHp{rv>sAMpYJ0__y~3=IDN3Iz23@A(uI2m%D{`T*k%`1AYt1Pk;56!!%e`S0@r0sHa|>-Ovu*6<bZ1pWo*7VHZX?Cb{Z6AJ|Q@&p44>-`fN8}{S|{tEp43GoFB4E^>2{Rs5=-ue9P`v?gM?*IkQ1MLdo_ZIQq9qj)d3;PfcIwSS!6B6$p|NadF0@n%{^X~op83hjk{ss&35De+-69g3x=?eMx_5AhV`xOTM0}lN6$^rE65CsSX0~8ka=@20V_5S$=4+9MmA?OSP)axAL*6i@>6#MuD@C5Pv67uu)A`tNb_YWA~3K;k63+V&#>KgCT{|F-F_ZJ8%``_{n1K;rJ+4tD~8UhFV4HWVQ`TpY$`rhdH*z)@h`ylif^a=zFCim3*Bl06O5###(BM#v6&*i8K2n+4-BP%HR^6?7y4JH5j`}zv<B>(af4fpZ^2?PZi5dQ+w7!2zg_z4iy_4W-9`sM2a{tx~P0QmO-`||Ye8VdIP@Dcw1`t$q#4)E^X8V?T+4hP~H8x#iv?c@Ot7Y6SW1q%l23Hclh>*(A6==k#50r&I!77qLP1?>_C^e_Yn5X<!f8UOO>*#G$c^%e&4`}PC&1nv49{|O-e3H<%#9VY?*1pnmy4EW{c2kipl0{8?9^5Gra=>q!z2pRtt4+{<O3jYZQ`urIC_4owq0SyZy5%K%&9|;l&*BIyW?JyDK3g{dL^z7pE>H-n+80R1J5B%O6`upAeHQ_h|_wp7P+w=kQA@%$k;R)*aAMpp|FX+iF5#A8v@ev>B_TUKu>>UIL_y@(~@$26M8TS1G4CM*o2Mq-80Q?FL0`La}?g9At0VMbE1p*!*`~BJU6AtGZ2NLuJ2KMLn1OWy60{|TX0PF<@ChZ6S{_6eX&G-fS6a)Gf=K>1z0s8p%B?k-p>IdEM=oj7}5c&}P@A2>h^9uX=^Zf<{=l10Q^#Bv@==kR%4G{<Z3;zH63ibF4^zZ)g_VWG&*%|=i4Ef^u<oyu)8uJMy5bX~M<ox#c@B{P(4*S~*4B$Ng>hbII0uB)f;|c-}1r7HN4EFj80|E;g{tfpF`4Qmy{{sRO75WPd1NaCJ?EnM-`v&|5{rT<u{PXn>F7yQs_u3322_p~m{0!vr_yhR>2m$~23J?183;Xy52nzfJ>+=ik{PP_85*ZT(?HnEe0RZyp2n_Wc?hw!e`y&Vi000N;9R4Kx6b13){PzU>?E?)R^&jpO-1qw>4)^}-2kIF1`u_3%@$>-u2>{;)10nPD^AP?D7xwG#5)k(A5&#Sc1qcNe^9T$6-RS!m`2qD2`UVUs5f~Br>g*N|`S%k63g`s?`}hO*1Ps;Y0sQv&2I&U&3G5FN>nA`Q@&+UJ;{ERY10ClM3>?`11MB?<77gy&1MK1b?i%(3;Q|ch0|)>X1@;CPFZB5Y`{WcW=o<?M@dNeo-v9ga`{@Jo4GQu31pE8-_%8<M4gDPa2kY(^{qpYE3K#wi0S^HU2;30o3ljkZ)9?%i-4zuW`1}L?^a%6v0R{j56$l65EZjBy902e%1`h1+=<);lCJz?_',2408061472)
install('tdq5x2',1600,1,'?*H}c2KfdFBpewF=pOtI49@xe4hH$%?fd@@{0I8@^#J|w@a!KC{{!j!1RMF?0_-0V@a^~q<?I*l2mSmJ2mk*30Q3&%Ec^=q00ILp0QK$S2Hy}K`~&L(_x1e&3>_Qq=pESK{Qctd8w~#(@An1%<oyl(00r>=^zHu(5%(AA^z{A+{`Cm}9Odoz8ukYk2@~5M{T=@2>Cp8D1N#i@<^&Y=0{{H^Aq)KBB^mbp5)b_j^!*PW1Kj)!{`36y1{)O*>Im)?@bLEq4-E_q{Sy+}0|ov4@%|q61q%i62l5jG@$~`h9|R8h4FCrS^ZEo91nm3+=L6{s5)2pj4J8lw79Z~Y`w00E0S*ZD>-+=p0sI;2{RaHt0vZM*2MYQ5|Nr#>`u7O{1PTEH{P+|L_302F`2!CR3;Naj&@AKh7|03-0tyJ^02vqX9P<43`VIXM_2>iP0u2}P{uv75>irAs`5pKC{L%dO@cixu4)YlE8yO4y0ut~3`ThS1{QVL8=mi7d?f?w>`T`Ky0p%0*`|$Gj{|W>4009RZ{{s>h1>ooMANBqF4&WBsAoKeB`0f`50`v?65d#bT4-E3>2J`A94i69{^yV+u7W?TR2l?#L6W{$22^QlI4BzeU{0$2D2@2co1@sXN3;+TJ{09FF3i|y06!7~7<M$Hz{s0Hs4(kW{`}6<v6Au9W0|of}_5%zT{{{0C>HGoy0UZqw^!N1Y4g~5B1ONXD?E?e)^7{Ym==2Ep^9AeV_3GyD3JLi16B6wO1q1{4`1}k9<tQ2g{|WT={|oT__V4-t8x-~p90>#q`u^?%6z2v0`2YX>5AOi?^$8sS{1D{>`1#rB{RaCE4KVfmBH{`V@DK?E_Ve}y4+Qt<<`3oh0Qd*-{rU$0^a1+u76={w`~Ugw2oU}R1^4X#0TucT`|}DO1^gNn{niQzH3<Cx0S6o(2Mq%P=>hKv`3d#!2HE}v>JS1H{14vd1pD_O0to#K^Y{7%{R#j54+sAE3hw>)`Tq(N@dx=5_UPvK5CZM(;{*2i4DJE;{2T=R_X7gt-1GDa`|$Js{R{j5`wa*e@d)|<0`L&$`uqS8=mzZo0~PH64E_55`}y$W8Vw@t^br#t+YST#=g<Zr81M7>2N3x35$*%#>f;>-{1NvB<1POx0_NSz4fGQI5i|S@3EAlc2j&DA^Z@q#1O)yK0RH>`8r1R}2<kWa3;^~52`T&a@!$OS0s#66`0W1v0{aUT2o?wl9Q^qG2JRmW1q}uQ=>P!&^!xVZ{L=jZ<O=%S5CR4F`78(T1`-tN3;pgR=l%ND3=;qZ{}U1b6V?0s`xx*A4E_E31Oor-76=aU^bQUq`TGL=-s=P)9N!55DE;992J$N60u&7G_4N`8=M5YM1px2T?EwA#^5Gfu)gJol9P9ok2IL9h9{BbbBiQ~31M1-91`HDl_Vok<1OoyK*z@uJ?eF6d{0sRE2L0~u65sy_>Fn|Y3jM(Z;1dxN`UKkk`v2_T{oMuqGwlJ{4D9R(@DU992@3}i@bvr}1^@)=3>ggo1oZ$35f0J@1_vY%3lP-w`2N!j3;g`nBLe>E^6dTmEd%uQ)d}$82m;s->;5Vk);I9t@(K&)zV-X;`~)8S0QJ`o_y_L##TLsP-WDVv_6{A*A`AcW03r|Y_YETK_Wc713H|c@-v|8m@%jt<3l;_Y>lGdL2n!DC`}_&_6ao?O`X%Yw>*LiJ4g~Z27WoDa_zMmLAPWT7<Ny-${Rs=*2jvp{`Rn@l7z_sf1^WFD1O5je`u7&?4GjqJ3-9>_|NRa73jq5U0sHOt0P+M73<&=U67B^N3<>-e1>Xnf7ZDKn4-5P6_X`u{0}|{5^4=d1-WdcE4&4s}76kwE>jU=f^y~lx^7I<~^5y>w69_Qw`v39g0~Ye|4f*v9^b+j*`{x7%6AA+v^XUZs4Ez1`0rUL>4GZ-F;QH$N(DnQl_xT9``1cCo3<B>3|M~F#`s(oa@!T31{0<Ni?Iacr4f^ce1px>9AMO?$8tfVF0sQ~?`Vt!s0qFk)?eqQq7zp|B',2576560595)
store_list("tds3",[MODEL_ID])
print("Part 3 of 8 installed. Run tinydata4 next.")
