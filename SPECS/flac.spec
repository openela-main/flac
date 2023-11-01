# Disable if you don't need xmms
%global with_xmms !0%{?rhel}

%if %{with_xmms}
%define xmms_inputdir %(xmms-config --input-plugin-dir 2>/dev/null || echo %{_libdir}/xmms/General)
%endif

Summary: An encoder/decoder for the Free Lossless Audio Codec
Name: flac
Version: 1.3.3
Release: 10%{?dist}.1
License: BSD and GPLv2+ and GFDL
Source0: https://downloads.xiph.org/releases/flac/flac-%{version}.tar.xz
URL: https://www.xiph.org/flac/
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
BuildRequires: libogg-devel
BuildRequires: gcc gcc-c++ automake autoconf libtool gettext-devel doxygen
%if %{with_xmms}
BuildRequires: xmms-devel desktop-file-utils
Source1: xmms-flac.desktop
%endif
%ifarch %{ix86}
# 2.0 supports symbol visibility
BuildRequires: nasm >= 2.0
%endif
BuildRequires: make

Patch1: flac-cve-2020-0499.patch
# handle end-of-stream when encoding with verification
Patch2: flac-cve-2021-0561.patch
# don't free memory that is still used after realloc() error
Patch3: flac-cve-2020-22219.patch

%description
FLAC stands for Free Lossless Audio Codec. Grossly oversimplified, FLAC
is similar to Ogg Vorbis, but lossless. The FLAC project consists of
the stream format, reference encoders and decoders in library form,
flac, a command-line program to encode and decode FLAC files, metaflac,
a command-line metadata editor for FLAC files and input plugins for
various music players.

This package contains the command-line tools and documentation.

%package libs
Summary: Libraries for the Free Lossless Audio Codec
Obsoletes: flac < 1.2.1-11

%description libs
FLAC stands for Free Lossless Audio Codec. Grossly oversimplified, FLAC
is similar to Ogg Vorbis, but lossless. The FLAC project consists of
the stream format, reference encoders and decoders in library form,
flac, a command-line program to encode and decode FLAC files, metaflac,
a command-line metadata editor for FLAC files and input plugins for
various music players.
This package contains the FLAC libraries.

%package devel
Summary: Development libraries and header files from FLAC
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: pkgconfig

%description devel
This package contains all the files needed to develop applications that
will use the Free Lossless Audio Codec.

%if %{with_xmms}
%package -n xmms-flac
Summary: XMMS plugin needed to play FLAC (Free Lossless Audio Codec) files
# The entire FLAC sources are covered by multiple licenses, but the xmms plugin
# is only GPLv2+
License: GPLv2+

%description -n xmms-flac
FLAC is a Free Lossless Audio Codec. The FLAC format supports streaming,
seeking, and archival, and gives 25-75% compression on typical CD audio.
This is the input plugin for XMMS to be able to read FLAC files.
%endif

%prep
%setup -q
%patch1 -p1 -b .cve-2020-0499
%patch2 -p1 -b .cve-2021-0561
%patch3 -p1 -b .cve-2020-22219

%build
# use our libtool to avoid problems with RPATH
./autogen.sh -V

# -funroll-loops makes encoding about 10% faster
export CFLAGS="%{optflags} -funroll-loops"
%configure \
    --htmldir=%{_docdir}/flac/html \
%if %{with_xmms}
    --enable-xmms-plugin \
%else
    --disable-xmms-plugin \
%endif
    --disable-silent-rules \
    --disable-thorough-tests

%make_build

%install
%make_install

%if %{with_xmms} 
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE1}
%endif

# split documentation
mv %{buildroot}%{_docdir}/flac* ./flac-doc
mkdir -p flac-doc-devel
mv flac-doc{/html/api,-devel}
rm flac-doc/FLAC.tag

rm %{buildroot}%{_libdir}/*.la
%if %{with_xmms}
rm %{buildroot}%{xmms_inputdir}/*.la
%endif

%check
make check

%ldconfig_scriptlets libs

%files
%doc flac-doc/*
%{_bindir}/flac
%{_bindir}/metaflac
%{_mandir}/man1/*

%files libs
%doc AUTHORS COPYING* README
%{_libdir}/libFLAC.so.8*
%{_libdir}/libFLAC++.so.6*

%files devel
%doc flac-doc-devel/*
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_datadir}/aclocal/*.m4

%if %{with_xmms}
%files -n xmms-flac
%license COPYING.GPL
%{_datadir}/applications/xmms-flac.desktop
%{xmms_inputdir}/libxmms-flac.so
%endif

%changelog
* Thu Aug 31 2023 Miroslav Lichvar <mlichvar@redhat.com> 1.3.3-10.el9_2.1
- don't free memory that is still used after realloc() error (CVE-2020-22219)

* Thu May 05 2022 Miroslav Lichvar <mlichvar@redhat.com> 1.3.3-10
- handle end-of-stream when encoding with verification (CVE-2021-0561)

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.3.3-9
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 1.3.3-8
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Fri Feb 19 2021 Adam Jackson <ajax@redhat.com> - 1.3.3-7
- Fix the previous change to actually build in RHEL

* Thu Feb 18 2021 Adam Jackson <ajax@redhat.com> - 1.3.3-6
- Disable xmms in RHEL

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Thu Jan 07 2021 Miroslav Lichvar <mlichvar@redhat.com> 1.3.3-4
- fix out-of-bounds read in decoder (CVE-2020-0499)

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Tue Aug 06 2019 Miroslav Lichvar <mlichvar@redhat.com> 1.3.3-1
- update to 1.3.3
- include soname in file list

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.2-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Mar  7 2019 Tim Landscheidt <tim@tim-landscheidt.de> - 1.3.2-11
- Remove obsolete requirements for %%post/%%postun scriptlets

* Tue Feb 05 2019 Miroslav Lichvar <mlichvar@redhat.com> 1.3.2-10
- rebuild again
- fix indentation in buildrequires

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.2-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.2-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed May 02 2018 Miroslav Lichvar <mlichvar@redhat.com> 1.3.2-7
- fix memory leak in parsing of vorbis comments (CVE-2017-6888)
- add gcc to build requirements

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Feb 03 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.3.2-5
- Switch to %%ldconfig_scriptlets

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Jan 02 2017 Miroslav Lichvar <mlichvar@redhat.com> 1.3.2-1
- update to 1.3.2

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Aug 10 2015 Tom Callaway <spot@fedoraproject.org> - 1.3.1-5
- add xmms-flac plugin as a conditionalized subpackage

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 1.3.1-3
- Rebuilt for GCC 5 C++11 ABI change

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 1.3.1-2
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Thu Nov 27 2014 Miroslav Lichvar <mlichvar@redhat.com> 1.3.1-1
- update to 1.3.1 (CVE-2014-8962, CVE-2014-9028)

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jun 03 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.3.0-2
- fix memory corruption in metaflac (#969259)
- disable slower assembly code

* Tue May 28 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.3.0-1
- update to 1.3.0

* Tue Apr 02 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.3.0-0.2.pre3
- update to 1.3.0pre3

* Tue Mar 05 2013 Miroslav Lichvar <mlichvar@redhat.com> 1.3.0-0.1.pre1
- update to 1.3.0pre1
- make some dependencies arch-specific

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-13.20121204gita43f56
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Dec 06 2012 Kalev Lember <kalevlember@gmail.com> - 1.2.1-12.20121204gita43f56
- Added self-obsoletes to help multilib upgrades

* Tue Dec 04 2012 Miroslav Lichvar <mlichvar@redhat.com> 1.2.1-11.20121204gita43f56
- update to 20121204gita43f56
- create libs subpackage
- split documentation to base and devel subpackages
- drop defattr macros
- add GFDL to License tag

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Dec  9 2011 Peter Robinson <pbrobinson@fedoraproject.org> - 1.2.1-8
- Rebuild to fix FTBFS

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Mar 17 2008 Miroslav Lichvar <mlichvar@redhat.com> 1.2.1-4
- speed up decoding
- CFLAGS cleanup

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.2.1-3
- Autorebuild for GCC 4.3

* Tue Jan 29 2008 Miroslav Lichvar <mlichvar@redhat.com> 1.2.1-2
- fix building with gcc-4.3 
- reenable some assembly optimizations
- hide private libFLAC symbols (#285961)
- update license tag
- add %%check
- remove -maltivec from CFLAGS

* Mon Sep 17 2007 - Bastien Nocera <bnocera@redhat.com> - 1.2.1-1
- Update to 1.2.1

* Wed Sep 12 2007 - Bastien Nocera <bnocera@redhat.com> - 1.2.0-3
- Make a few functions hidden, to try and avoid textrels
- Disable optimisations on x86 for the same reason
  (#285961)

* Tue Sep 11 2007 - Bastien Nocera <bnocera@redhat.com> - 1.2.0-2
- Update GNU stack patch to cover all the NASM sources used

* Mon Sep 10 2007 - Bastien Nocera <bnocera@redhat.com> - 1.2.0-1
- Update for 1.20 and drop obsolete patches (#285161)

* Fri Aug 24 2007 Adam Jackson <ajax@redhat.com> - 1.1.4-5
- Rebuild for build ID

* Thu Apr 12 2007 - Bastien Nocera <bnocera@redhat.com> - 1.1.4-4
- The byteSwap symbol shouldn't be global, reported by Joe Orton
  <jorton@redhat.com> (#215920)

* Wed Feb 14 2007 - Bastien Nocera <bnocera@redhat.com> - 1.1.4-3
- Also include the new pkgconfig files

* Wed Feb 14 2007 - Bastien Nocera <bnocera@redhat.com> - 1.1.4-2
- Update link-ogg patch for 1.1.4

* Wed Feb 14 2007 - Bastien Nocera <bnocera@redhat.com> - 1.1.4-1
- Update to upstream 1.1.4

* Tue Feb 13 2007 - Bastien Nocera <bnocera@redhat.com> - 1.1.3-2
- A few fixes from the the Fedora merge review
- Remove the static library

* Tue Feb 13 2007 - Bastien Nocera <bnocera@redhat.com> - 1.1.3-1
- Update with work from Matthias Clasen <mclasen@redhat.com> up
  to upstream 1.1.3 (#229462)
- Remove xmmx-flac Obsolete, as we don't ship the xmms plugin

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.1.2-27
- rebuild
- Try building w/ glib2-devel

* Wed Jun  7 2006 Jeremy Katz <katzj@redhat.com> - 1.1.2-26
- rebuild for -devel deps

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.1.2-25.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.1.2-25.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Apr 21 2005 Warren Togami <wtogami@redhat.com> - 1.1.2-25
- Fix buildreqs  (#154649 thias)
- obsolete older xmms-flac

* Mon Apr  4 2005 Elliot Lee <sopwith@redhat.com> - 1.1.2-24
- Removed xmms-flac subpackage

* Tue Mar 29 2005 John (J5) Palmieri <johnp@redhat.com> 1.1.2-2
- Rebuild (flac picked up a dependancy on it's older version)

* Mon Mar 28 2005 John (J5) Palmieri <johnp@redhat.com> 1.1.2-1
- Update to upstream version 1.1.2
- Replace flac-1.1.0-libtool.patch with flac-1.1.2-libtool.patch

* Wed Mar 02 2005 John (J5) Palmieri <johnp@redhat.com> 1.1.0-9
- rebuild for gcc 4.0

* Wed Feb 23 2005 Colin Walters <walters@redhat.com> 1.1.0-8
- New patch flac-1.1.0-gnu-stack.patch from Ulrich Drepper to mark asm
  as not requiring an executable stack

* Thu Jul 15 2004 Tim Waugh <twaugh@redhat.com> 1.1.0-7
- Fixed warnings in shipped m4 file.

* Mon Jun 21 2004 Colin Walters <walters@redhat.com> 1.1.0-6
- BuildRequire glib-devel for xmms plugin
- BuildRequire nasm

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sun Apr 04 2004 Warren Togami <wtogami@redhat.com> 1.1.0-4
- #119551 flac-xmms -> xmms-flac to match fedora.us and freshrpms.net
- Obsoletes flac-libs to upgrade smoothly from fedora.us

* Thu Mar 11 2004 Bill Nottingham <notting@redhat.com> 1.1.0-3
- fix x86_64 linkage (#117893)

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Aug  6 2003 Bill Nottingham <notting@redhat.com> 1.1.0-1
- initial build
