# CalcGPT 3 model installer 5 of 8. Run in order.
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

if installed(5):
 print("Part 5 of 8 already installed; skipping.")
 raise SystemExit
install('tdq5x8',1600,1,'{QUwA0sjT*0s$Nx{>vmm+!Gk)_UhItx)TiU{}Bb@_YxNX;|lN$-T4Oh^8E_y3iA&A0s{j40tE^T_WcU{{`4Cu4gUx4DE|Qg>HY~C@89_20{R0A>=ott1OW;N{T2oX^V|UY@$VP%@(lX`3MB6v-S_(W0TlED1pp8v2mtE``}ye_^X(7z8w&UG<plTn_yhh8`3469{|5%t3<2#7`2`X4{qhY22-^Dj2>R;^^9%d?3<UAy4*&M{^#uO~0t4|4@A?iN0Ri~<>;Uru0Rs#51R(+m5d0PL1Pbi=2k+wZ0{8(J4H57C^!ybC{{tEX`ql0K_74O2>I>ob{sHR*`u!9b00Q$B6#EYg|NIRC^bZB?3I*=|0P5@W5fk?O1Pbo-^ZgO;0QMyw`25=b{|W*1^9btw`Un;s1QPrJ^#k(;3H%E45efwd;Q1950qphx^$hyz{~`Pt3Hs0a3<&xJ2=)>6{R<oW<OTi&3+)gC4hH=6?GgI)`1b?$`tcV1`tJY$?Dh=y4JG0a#1a1{8y*b*0{8M3``!rp5at-~2lN8{4h`u7{S5UN`u7+Y@)-E}5drB2{rL&*C<6T%;`Hdw-wOQM7Z?=e*#_GJ-1qeB;tu)`{~R~<0MY9D8Rh`|^Dg88_2?TI?+5t&<N_W60{#R05*r2d3-I&$>=_3N5BLW5`uhs|?gsz-^6&TS2m0e61Ka}l>k|J2{rd0$@aqpH|NR;20Sxc!<NN~x3ibL8;`;Xc@A&))>;3fv{wn(d3il5D`U3_O5Bdcr|Nj=+0s-gw_9Fum3()Y|9u(N~_!a>!;u#e24I=y$^5*#v82#@9_5K_C<m3bb76$qL;sX)`7a08B{R;W;>h}fr3jgp14f_o3`uYg^>ktwL{Phz90sa3Y>Hz!@`S9=o=neA!7bz197X$AG2^sbS4EFs5`u^=9*!=VP=Pv06{w)?E3kVDJ6awV(5bqK55D6Cd@Ann`2lx*N`|$<;2lxc^^#}<L5&Zk~4E`1!2ngfw?FHNO^#1Y==n&=%{SW&23jzB7_U`}tC>HnX_Xzd*{rcAX{PyVu^7Z=!?G^R}^#2C~0}b^A0t5B+0`USC*%a;;`3Mv<`w0%^2><U13JCu44jBL${UY1#1^DO|1sVnY?C}Z`^8*M9^!f4h7z*k12LAf@{1o>K?)l;2`U>t9^#BGA`~>bC3J3uD{pko0?e!n>?+Ez%0_WiW{ucBQ6c!#G?fLB60_^=6^C$uQ1sv%F`ts@y`|J!75&s1Y4Eg;B`U4C973~8E;r#p!5BL4~?CSs(2O<{>0rdtB>j@MC5%w151O)o@0{s8{5$Ns#0`db7BLoKq3kC@y?E(et1PcHf)ARe{5fSqH{OS-3>=XL?B@GS+3ibsE{`n#p`r`!v{0IR70u0j==kE<3{saT(0P+p%1NIH_`3e8<4(|o;1OxIA`t=Lr8zvO|{s|in2owSH2><y501Oc8-SzbR4Hpj-{rc|r0U8th_y#BV1nLq5AP)Qq3IGNG{{86v_Ynu?{3r?T6!QoP5&!M`0RROQ@+H*4_t*>@4HVf0@&y(#`}OMN5aja$^y(e*0_#H$84w8m5dZ-f?d1334CD<30~HGf>htgp0R;pO0L&ZW1^pTO`Udv(0pb}O4+QlH3ljtx`}Ph2`uqMDA@}q7`3&(8^y&NS1q}}S2mt-$^#%^)0~`Ja0^|eZ?FsDd3@rE%77`EW;~5<Q`~~;^1ql)D3JeSs1I7Uh3=IMbAN&OsAx`2L3;_M~@Brl$3H9*s5D?P|><q;j1uE?U^%KA>@&EJk6bAti?ZFECED#6k;|2i!01*ri-U;jt9Ulb@{_6$}_XP_68ub<o3;F@?{0IFI{S)uy{NVQi83+6a|NQ3r1oZ+C?Gx|b+5+$G{|5vL&jk1k(<lZ1`|lhR+w1b;3it>Q5Ayj8{0ssl!7k7m?J(m5-~#sl`3vqY<Om1+Cmj?eCIJ-s|NiwE{0`gy0`dj|`vw3H2k!j&5&Z)h4iDw<4($RI2IL9q5eNPO3ilKd2?_%X>IM$>6cPLQ',2383087877)
install('tdq5x9',1600,1,'|NSZY^#<kqARPJN`{?)g1q2KP`0EJv3<eM)4gcQv7X%3U@e1hx{@oN9{u}xF(FPv@><tY61`Y`Z^ZW+&1^L=4?*irR9Wwa|^7`rq3<l5s0txE_{_+U{>EQkX@DLXk2MF)<^8xV*0vz@I{RRE;1NQ&n;|cE!^y~2q>K*wK^CA8A`{)%5;_LnS82l9e1PBuA`~eOV^z`Nf=?~-;5c&NW=>_gI_w)?=9oz^H_u|<90r~g}{T3Vn`SAVz9R&6Y5C8u75Apy82OjX|2?PrM@&fo23ibjU>nj2M>GA>-@&Ne`^%V5~;|vSu3Iq)r?FaPt^fvne8Rq~1`v40C2KN>k4fpj34gKK>@F(&E0rVdx1^YDp2LA```4S8A79jrb1n?0C4fFF7?C}8Y1`!hs`uz(9{38wc2Kfi?`SRxW@dp3->jB~L{S(>%@cIV|`1k!74E_@T1n~zH3-$pC1Ofv5?fL}+2od@W|Nj5%3=9bR2>a>_5)1|r_z4IQ{`dU!76$j~=MLub0R{c}0s9L2`u_s<=MC}u1quQf*Z%Yt5jFAt9q0ZC<n9yr2JH_I1Lo@Q`w#II>k!x#1NZzK^X~WbAQ9y0_4^MA69EbU3-BH6;sWsf?;hvj2I&jx{S)*N_W%b51^fyQ5Bn4aDE<5W|NROG?ga`A@B;Yj0~P)50NM%*@dg7BEZ+MF_ayO0{Qwl;9sLUs<ofL9`xyWM1o!&#_W0}S2@m-m;}Ys61mGM8`5glP=d1%K{i_fd4hsD1{pTJ71@s}^3iK1>0PFk(2mIdy10?$m{R}1Z4dDOz{P_g<=nm5Q{15p1`u7JA1OfIT1rP-a4)zrI^!ok?1oIB}@&x+<{306)1=<=6_6Y+V5cw1U2MF!(BJ2Y5>FNm==mhon4)g*5>Jakp{O=6;6b}FK?e_i*0Q=n_^#1ST5e)bc=l#<76#?Pe2ki<M1PJj0`UV2}0PYv_74-N1^$+p-{t5v00tN^E1^)r%><jn=3JVAN?D_Zp2^<g!6Zr-V1qKG{0P7+X3<350?id3G`2pVN{sjL0{r?RR{15FF4+RSY{Pzz9^5p>;^91w=0R9Ey)F9~t`1cJ600RUG5C|*V1`-?jFaH7v{rLqK{0ayA>iY=*?HB6u2l@a5{|gHS4(luU@&D}y{2BZ3?A-qM01*Bj`~v_52mKEb00Z~+6!HcU`0*C@6BzgN1qmGl2^0Jx_V@z&D;fz2?fU=~1qJa3+V%be+z9~u3>g6I@)Z*C6$%096aeQ5=-mkG|M%Pl0W-}b6963M7yaxX@8Avr`w0#a`v>dc5AyOV5d8fL_5kb`_UHTh1?=w$6BY>X0ucY|`uGPA@C*F`?%x$64*(7JtQFM!3JVPV2=@UA_w)l6{Snq82p0I-)GEmT3+ep;3?l>e6#p{Y7Ypn6{vq${1^oOL2I}i55&{wS00994`uY+39p3)|8teW4@dNw$`T`FI0R#R5{Q&;?0TBEQ2mAQ{1`YQ1H38fF?EU^9_Spx{3+VY2`vvO+1n(CA{0{^K>jeWE_x|<<?iu>t3?B^r5A*K+1^4s>5A+t@2nP%LLjBzn1_Tiv0tW&F1PS^H`Sl0$^WhW>-3bdL+yML;1_uup{{jy4ASU-5`u6(>`u+F*5e*U~1pO`c_!sjR1}_2!_wxJ%{QCC-{SpEH{_h#*{R9mq_~se>&G!Kk0xkpG66FW#01n?6{uuu45Bc{E0|)Q|1|RDG|LyA&`~40f7X9=A3JUHM@A?b(`~(OU>HYc={RIFL^al4N6(Ir?0QLnF1NHdv2=)yK6%Hld5*hYP_Vcy}>krCVu<ZNu2_f`2><St52ig?W+u8g61_=WB@b?Y~`4AEc{R;>U^)34h7y1A7{1@Ex2kHF*1ndR(`1S_}|N0jP0UQkl0si*=8XOz_@(cj*{`b=&2=of^_8cPv?F<PK<RlaG1Oe>=02v|w4ge1T1rZz-<@@vi5Fy+15F7gy@)QaI4EYG>00R#C{s{#T-|g)34=dsc_1_Z?2mKBJ1pgHm{`(6E0rCqO_5lb7',281279859)
install('tdq5x10',1600,1,'00!Fj)G+k;65Rz0|M&*w`xqDJ{RA@j`~2+k3mNhP`S1Y$^ak_z_VV-X3jYEN{|4s#2m2TI_6q*(_xc+o1PK}K5e^dl4F?JA4-*9b^#>RK3=RC|4D0{*|LzVC7XkbZ{08*%3i=To0T}fIK=cLr>;MrL_WJPh{r>U({Qv;z{_6<}3lkLk9`Wt+1^4&<0o3;F{PXhj(hCP7_9@=j4e<s1{SgH42>1pB`Sjrd0sImn5c~xI68rcJ{SF8C2m18?5#k6300#j0>jMG%94H6&_!I*9{R{033-bW`{sQU)3G?&;^yLZV3Jdq}3I-DV5CH@Q0}TZD8XgVz3;quf?*;@C?E?`M`2g+#5eEb9@(KMR5efPS|NGtx3<34{3h3?u_x}tk4F~=H4EX{F`tJwz3?UR1>i-S*`v(I51M3C*4E_558VLUU{Q?LC1pyiv2lm(Q`1$<#2<Zd!{R{yQ5dIkn^92Y8^Zg9=AP@`=1^Ds-{R#W~@EQ8)6aVrm@Anez?EcsQ1^_Vq_5a)n5Bu{G4ekKr81nk~{Qesc0RaO23<?DW4jl&U@8SUo_6qj(>K+0S`ydAR1=|%4>H7N^4f7Zk1Q7h>>;3Hf{0{gJ4GsV41_B5I{R9*a@d6F`01gHj-U31S1Ni*}2@ww({{QR+=k5d#5dZwu9{=$J`V|up+!y=%`rH-x3<mY{>;~)P0RHy@_V5h#0r3L>`vD34`uqwa>ihZN6EO`A9RBwN_5uVN8}tJn1n~pz0r&~~@)z{+4e}Zl5dir71`GZV9OeZ80`C0%{p;)m1O@&d`VAfZ|K<Pu6a?=B3H1N{8~6Mb3K;eE{Tl}d<`U%Z{|Vd#`vnOO1mo)*4gd)G{OSt>;{h7?3j6&L=lTWTAS3+`@BZr){RIF00`e9Z1_%NX_XX?+1T+Wu6Z-4&{{8s;2mkd00sRd8_!<Td0OSk<1p5W<_5tYn0}=fU4*&)b>lOR-3+x{a_#f>4-`fuI_Wa)z^exUB5&9G57y<SM^ymur0}2-a;PnUb2n`7f=oa$;2O=2|@!k|0{00605%U5H00hqR2>Isy3g8y$4D$8#_x%P6`vUj<`WgxO7a9NkCh+?o`X1jF`2GFx_zxKj^8x7f?H2+44Ho+k`4|c60S5&C{TlP~1@R6D7z6qQ2o?Ya5CRMO`v&~~2H`mH`UvR*4m1Ym`RMin76|<D0tER64fzoW76$<F9RCd!0ssc@^!WJ&2>A*B5&iT93knDQ3LXdk`SkDv1p(v+?F$3?5+)Y^1^EjP`~Ua(4g?DR{{R*F_Tm8a{PPI;^8oMy{|NB|3<w4Q=oAJG1qcNP@cRt$3ikdN@f!E$5gPsq6!YK(2LSv62J{g400jmMC;ssS4A&DP?Go@A>jVV%`UmL#_7fEV4ig9V3i$j2@ecO}4B`jy5gHQ#2Lb}-`2q~+3JK^F_VFb36aDu2^bYO<5Cii31q1*O_1XCQ0`CPC{T34N@C)?*2?+-i-wf^j5*PFf0pb<@_x}3x3i=ru3-t%<1_BBF{1E8<_}~u>5(Dl74HNkj|K<k;5cd4<?c)6T4)Op6*bfB@@gD~Z0|piU?ga7j3;Or?3;^Bw_x~FE@7D$8_yG782MqK74G`V%1K|Y(AsP)C^za}3`wIp972@*<>+bXK5(E4S{sRB&1Mm_Z2LI~x>+k360RZ(4|KAb*1_Jr|{0{~K`UD064F3TD_xJS;4Gi-G)A0BN?gRb(6bkt7^dSWW1_J~33IhKL4E6a43>MS)@c9)L+zR;L7zX?Q|NIC592D^M_zUk9@Ac#W^9u|K_7d^_>H+ld{XPl!6bT^j5+vOU_80#c_aYn=13U~h`yKl22n6yY*aR8!CiW5x^79A$1_1={_v`--?+yC}82k730}c-b1N9mh0~YlRApH#v;`tlq1KI@V1ON~T|L^_s_WcFv4kZBY==A{l0sQO)4e$gJ1{VhZ1pgiQ==lZ$1^O2q1qtdD=M?hv@d+IS{T28x#1H@Y{`J>D`}G&=H1ZY?4iXvs`v2Yb8t&%Q3jPHu91jWU',2369518894)
install('tdq5x11',1600,1,'1L^<{85|HC0N*X_4i)zL4<+{n_XPpu4G{+a=@t_G{O}g(2Oa|x6YLT7`wHCr0`Bw%0Pqe75d+`-{{sX31^x&T3g`d_3;+)z)fVk20O|=f1^g@Y@Ce>G2n`MC5HSE9_2d8Y3jzfC3Ge&$^A8I84*&rL3i}cD1ON~j3JT!<3H|gE6%^w60`UMW@C@?cAQ=7*1qJ^73Kb6r0uD0v{|Ef@8x!gX@e=GE-v9&*=m7HR3KQ=V1Mw&G0SW{I`xoQT4eBQTBL?&S1ODs%{09vV0PFzJ=<x?0029qD90>*H;V{Yr2loXO11tmO3<o6K6$}#xE$aFI<LVR-_6rOR?*!}s@&EJY1ojRC1rq)9=no7F1q})u2><%xD=hm9=kM+J^z;Sw4eJpv2j>&#2muWY0Tbrw`Q-``4<rl*5)%On{P_z8B-RBS0rC0n@B{uJ^bZ-`4g2;35A*W(3G@8-0}Bck@dEJQ`vcAH<MZF({`Bl76buRQ0~hSx0{8_2_3{Pp9tbSz>H!4_5AyH-_5tSr5CZcF6$tqC78)EE4;u{h0uKca{O;=&1n>?g3l9+%5B>iJ@d6O&0PFq<2kQL+{`w04<OBit5g+~d`UV3M`wIIL2=e{|1oi>y4-N(C2I=M(2lDzQ<N^%x@DBbM0s{vAB<}GO{qz(J^ZX1P<pCD?_XYd<3kV1a4h{VV1OpBV4C3wf3GfFS0_PR+6b}6C0rw>Z`T_F*?+FF>910Bo)%^eY0~H4!-SqqR-x>J{2m2Hd1OE8v2Ll)!5#b;8{tN{L_zdhM1=<N53kVAU5f}Ib{`3z6AlCf^4G;+g`U3w4*AVIR93lb{_v8@=1M>p)3GfXE`Skex{ptt(5a<8|`u+_j0RkEJ0}clP2=oU2ARiMB3*{{C|NrR<4;uOU;^z<q4hski{_*|#2mT8O3IZGH00R&c=qw1?_2~}+ApPV2{1X2X^Xd=y|M&b2>gxIi0U_N4?+W$=`Y7ZB9{&v*>IVS$2>ci@6D`c@{QUm^@(Jtn1{DVs5eNea`3eCU0R#{81o8+L8vYyl`TErI2=wmi0{06T1_}5B?*H@+4iOF;1@!LV3;qQN=lb~?5cUZe=?v=v=k5>~`Q`-p^B4sQ4Dmhv_VNJ^4Hoj~>){Xn{t5IL_xt$;2KfvF9Ru|B1pxZ`0rUd|6#w%A?-KF%?F{?y`~V0F^8*Xi0{I3J0SNv8=>`bv3Kb0y4+#kW{s#321p5>A`}+9*`w#vG`RnBa1_t=@2oMSd_!k8o?)wM(_T~c^@Z$s+1NQOz>G=xz{4M_l3H=Ng?*Ib%2?hlV`2r^O3>^;@^%LmK1KtWH5cc@`?F9T9^YIG-|MC4G^#1n^!~X*i5FGy9@COz4{|@{D>;&od5cBf#1qbr>4*dHE1LX(r6bbt4{00*S`VsmC{|N&Q3mF3M_WK6;{R{c$^zZ%R9TNrt{__JB2mkX6`}-RI_7?@(6YT#2`3U<W1>E}J687;5_z?x`@bU}-3l|at;sy!z`vDLp;raLh_bmYq9P$eM>j?b{2=@ma0saN@{|N{V>-*RE?g;1x0`vU|_x;%-2^k3f73vA~FZ?0#0}15(_x<Yr5)bVi2@dxN67v52{s}GqB;ytE_XPU({TAp4{|^KD01_1k?)o17`3n;5_yPeS+XegK_xbzr?e_Hq`zr|b5cd5S5BvTO{qYkC1orjz3;quF>>T<K1^*H%_#ONH*a;B{@AU-${R;dFCGQQ@)BFY!;`kut1OWCG>Idx7`V$HL4+1d?9}U~?<^}l(`vl<p`0L~X_6Q{l?jY|668Q%E`~Lh5@$?7p4kiTs>-G-w1_k*A4)7N83j_7x{Rui6_4*R|KJWk$+2I)r<o)yx_7LR@0sHFo_4N=2^#B3?<^>q|4)*FI@AC=o6dw!|`}@!Q{Qdm;1^)T*`U~vx`U@5N<^<db6bI@33I_%h0tW6Y{`Ln71@jFG5$XK)@*Vaa3gRc#91t7<<^T)_1p4|F4i54I4-5eR{1prF{QmYS2?z}%{ss{O0~6s3;`k8v69E4S',3850953278)
install('tdq6x0',640,1,'!+*(O&B4aMyv)qO!n?=A%sCPy4k#2CD>LpA7#kG{{st2h?*I(&69n@H04e?P`S$Ma6cGgzA{P1uC<7D({uB`&AL|VPCI$cx@aFve@9zTe9|j2){rE5Y{pAYu`Ss}O^!@(?1o!vs^9>mI0OlJ4>+uZp2MFc?2;&DL-|z0?@96;U`t<4f0`>YA==S#l`t}a$0rvXT_VMHf{Rj2r`3VRM2H@=5;sWLX@a+`){P^ee*dO)h?D^aL`SRlg?biV4=i~MB*Y581)D89G<>K`40^;-f+UNxF{`B$Z0Q>6h{O|to;oITr+70yD*!Sq|>E!m~^Y$9`-tYL^-2~h9;qT`8@#x>y+WF$`@$>ZP<Lm?8>IDGx<M!S1@9^s0-{R=y{_W%V@B9Vw-39dZ@cH8Q@8a16`rFp->GbH|BPs_7-s$Y)(*xVi@8j>@`S<Ae@y+Yg1NY?I>iqBW?&<mG3-;IR+4t<*`PSao-1gq}>FD*;0`2Sz-{$J&^YQ!8?c4wH_wM20_XGIo<K^k$?(fp^@89VI@BHZV)B66)1?c<m+VuAC_2lr_>*MJ2^z!7{+uQHa<oNdR-1+L=;OYY5=-%|$@Yws?%l7B<=H=k;^XUHQ$MW6>0P^zb?&ap)_}1s^?eW~_>g@vK=<f09^6Jjy<kRHj-qYmW+~e8D(Eat_|MBAK=<nU);`8C{`sefh;@jTO@b}yC@bT>9<K^Yw;qC3`=i2S;=IP+&`Q_;G<Hzam?A6N3_we)o=HcP!-RkoB>EG<+^6Ko{=<?>@@8jzQ<>~a~=H=k~@#yIC`O)(5^!N4S>+ap<',3101615120)
install('tdvc0',800,0,'JaA!TJ^(y*ZfiaOJYsKiJ^(yrZ*x8XJauzray|e&VRLh7b97;DbUpw)VPkY(X>Mk3J^(ynV{~6}b!BsOX>V>m06bx1bYEm?a%E$5X?A5k06bx1bYEj{ZEb0EZDnqBJ^(yrZEs&=VQg(a06b-FZ(m_<XJv9e06b-FZ(n3-b7ysPbUpw)Wo>U?W@TY=J^(yrZEs&_VQ_GHJ^(yrZEs(5VPrl4JY{WfUvqVGaB^vLWj+9TZ*>4^0CZ?&0CaBvVE}1#0BLgoXkm6`0Az0fVQypqbZB980B>dhcW7aB0BLRjW^Zx;VRB^vd2e-c0Apcp0BvOecVz%=c>r{1X>$O1Wpe;*X=`NwXm57_Vs&%?Vr2ktZUA9oZ*_D4b8i4?Cv5<CX>@1+cV%pB0CNCobSHBFZf^i|XlZV10B&z|0CZ?&a%BK#Z*OD(cWG>F0Bde<cK~5@0C#V7Y-9jxb#rt8Xk~I`0Az1&Cv*UJVRHa-WnpY=c>rf+bO2#&Yyf9(0B>jjb7f@!X=VU#Ze;*>VQzE)aBO8^b7cT>X=iA30CWI$Wpa4{Xk`F%Z*64&bZB98CvyOFXk~c-WNBmoXK!h4X8?3*ZDjy+b#i3@ZFOU40CZt%WdLDq0B&VvWB_h&cK~l|0C#A40CaC}0C#9*ZUAF%b!=n+VQv6*Z~$+0bO3L4asXy>Z*2f*Wo&Q&VRHa;Xm53FWB_z%VQy;xZ2)3rWo`g-Xk`FtCv0p0XK!=>bZBL60AX%<0Bmn>YXEO@0Ap`$WdL_*WpZTzZDDx;b7^t_XL4m>bO3i~VRR>R0BmJ+0CZ(+Yyfj_a&mb9Ze@1>ZDDI=0AhIncW-iQ0Bvt_WdM0)VQ2tpCw653WN&T&Xkl{zbZ=x~c>rlAWB_Jqa&vS5bZBL50AX%<bZBXAX8>?zZ*Xj70BB)k0Az1va{zQ`VQy=40BB`$0BvDzc>rv0Zf5{!Wo&G30C!<|0Bv#rWMO##ZEtdJX>Ml#V{dhGb7cT@cW(e}Z*%}>X?A4*',4208330941)
store_list("tds5",[MODEL_ID])
print("Part 5 of 8 installed. Run tinydata6 next.")
