#
# Conditional build:
%bcond_with	luastatic        # build dietlibc-based static lua version (broken)

Summary:	A simple lightweight powerful embeddable programming language
Summary(pl.UTF-8):	Prosty, lekki ale potężny, osadzalny język programowania
Name:		lua52
Version:	5.2.1
Release:	0.1
License:	MIT
Group:		Development/Languages
Source0:	http://www.lua.org/ftp/lua-%{version}.tar.gz
# Source0-md5:	ae08f641b45d737d12d30291a5e5f6e3
Patch0:		%{name}-link.patch
URL:		http://www.lua.org/
%{?with_luastatic:BuildRequires:       dietlibc-static}
BuildRequires:	readline-devel
BuildRequires:	sed >= 4.0
Requires:	%{name}-libs = %{version}-%{release}
Provides:	lua = %{version}
Obsoletes:	lua < 4.0.1
Obsoletes:	lua51
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Lua is a powerful, light-weight programming language designed for
extending applications. It is also frequently used as a
general-purpose, stand-alone language. It combines simple procedural
syntax (similar to Pascal) with powerful data description constructs
based on associative arrays and extensible semantics. Lua is
dynamically typed, interpreted from bytecodes, and has automatic
memory management with garbage collection, making it ideal for
configuration, scripting, and rapid prototyping.

This version has compiled in support for dynamic libraries in baselib.

%description -l pl.UTF-8
Lua to język programowania o dużych możliwościach ale lekki,
przeznaczony do rozszerzania aplikacji. Jest też często używany jako
samodzielny język ogólnego przeznaczenia. Łączy prostą proceduralną
składnię (podobną do Pascala) z potężnymi konstrukcjami opisu danych
bazującymi na tablicach asocjacyjnych i rozszerzalnej składni. Lua ma
dynamiczny system typów, interpretowany z bytecodu i automatyczne
zarządzanie pamięcią z odśmiecaczem, co czyni go idealnym do
konfiguracji, skryptów i szybkich prototypów.

Ta wersja ma wkompilowaną obsługę ładowania dynamicznych bibliotek.

%package libs
Summary:	lua 5.2.x libraries
Summary(pl.UTF-8):	Biblioteki lua 5.2.x
Group:		Libraries

%description libs
lua 5.2.x libraries.

%description libs -l pl.UTF-8
Biblioteki lua 5.2.x.

%package devel
Summary:	Header files for Lua
Summary(pl.UTF-8):	Pliki nagłówkowe dla Lua
Group:		Development/Languages
Requires:	%{name}-libs = %{version}-%{release}
Provides:	lua-devel = %{version}

%description devel
Header files needed to embed Lua in C/C++ programs and docs for the
language.

%description devel -l pl.UTF-8
Pliki nagłówkowe potrzebne do włączenia Lua do programów w C/C++ oraz
dokumentacja samego języka.

%package static
Summary:	Static Lua libraries
Summary(pl.UTF-8):	Biblioteki statyczne Lua
Group:		Development/Languages
Requires:	%{name}-devel = %{version}-%{release}
Provides:	lua-static = %{version}

%description static
Static Lua libraries.

%description static -l pl.UTF-8
Biblioteki statyczne Lua.

%package luastatic
Summary:	Static Lua interpreter
Summary(pl.UTF-8):	Statycznie skonsolidowany interpreter lua
Group:		Development/Languages

%description luastatic
Static lua interpreter.

%description luastatic -l pl.UTF-8
Statycznie skonsolidowany interpreter lua.

%prep
%setup -q -n lua-%{version}
%patch0 -p1

sed -i  -e '/#define LUA_ROOT/s,/usr/local/,%{_prefix}/,' \
	-e '/#define LUA_CDIR/s,lib/lua/,%{_lib}/lua/,' src/luaconf.h

%build
%if %{with luastatic}
%{__make} all \
	PLAT=posix \
	CC="diet %{__cc}" \
	CFLAGS="%{rpmcflags} -Wall -fPIC -Os -DPIC -D_GNU_SOURCE -DLUA_USE_POSIX"
mv src/lua lua.static
mv src/luac luac.static
%{__make} clean
%endif

%{__make} -j1 all \
	PLAT=linux \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -Wall -fPIC -DPIC -D_GNU_SOURCE -DLUA_USE_LINUX"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_libdir}/lua}

%{__make} install \
	INSTALL_TOP=$RPM_BUILD_ROOT%{_prefix} \
	INSTALL_INC=$RPM_BUILD_ROOT%{_includedir}/lua52 \
	INSTALL_LIB=$RPM_BUILD_ROOT%{_libdir} \
	INSTALL_MAN=$RPM_BUILD_ROOT%{_mandir}/man1 \
	INSTALL_CMOD=$RPM_BUILD_ROOT%{_libdir}/lua/5.2

# change name from lua to lua52
for i in $RPM_BUILD_ROOT%{_bindir}/* ; do mv ${i}{,52} ; done
mv $RPM_BUILD_ROOT%{_mandir}/man1/lua{,52}.1
mv $RPM_BUILD_ROOT%{_mandir}/man1/luac{,52}.1
mv $RPM_BUILD_ROOT%{_libdir}/liblua{,52}.a

install src/liblua.so.5.2 $RPM_BUILD_ROOT%{_libdir}
ln -s liblua.so.5.2 $RPM_BUILD_ROOT%{_libdir}/liblua52.so

%if %{with luastatic}
install lua.static $RPM_BUILD_ROOT%{_bindir}/lua52.static
install luac.static $RPM_BUILD_ROOT%{_bindir}/luac52.static
%endif

# create pkgconfig file
install -d $RPM_BUILD_ROOT%{_pkgconfigdir}
cat > $RPM_BUILD_ROOT%{_pkgconfigdir}/lua52.pc <<'EOF'
prefix=%{_prefix}
exec_prefix=%{_exec_prefix}
includedir=%{_includedir}/%{name}
libdir=%{_libdir}
interpreter=%{_bindir}/lua52
compiler=%{_bindir}/luac52

Name: Lua
Description: An extension programming language
Version: %{version}
Cflags: -I%{_includedir}/%{name}
Libs: -L%{_libdir} -llua52 -ldl -lm
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post   libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/lua52
%attr(755,root,root) %{_bindir}/luac52
%{_mandir}/man1/lua52.1*
%{_mandir}/man1/luac52.1*

%files libs
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_libdir}/liblua.so.5.2
%dir %{_libdir}/lua
%{_libdir}/lua/5.2
%dir %{_datadir}/lua
%{_datadir}/lua/5.2

%files devel
%defattr(644,root,root,755)
%doc doc/*.{html,css,gif,png}
%attr(755,root,root) %{_libdir}/liblua52.so
%{_includedir}/lua52
%{_pkgconfigdir}/lua52.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/liblua52.a

%if %{with luastatic}
%files luastatic
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/lua52.static
%attr(755,root,root) %{_bindir}/luac52.static
%endif
