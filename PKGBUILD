# Maintainer: YoannDev90 <YoannDev90 at users dot noreply dot github dot com>
pkgname=awesome-kde-system-monitor
pkgver=1.0.0
pkgrel=1
pkgdesc="Custom pages for KDE Plasma System Monitor with auto-adapting sensor generator"
arch=('any')
url="https://github.com/YoannDev90/awesome-kde-system-monitor"
license=('MIT')
depends=('python' 'python-gobject' 'glib2')
makedepends=('python-build' 'python-installer' 'python-hatchling')
optdepends=()
source=("$url/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$pkgname-$pkgver"
    python -m build --wheel --no-isolation
}

package() {
    cd "$pkgname-$pkgver"

    python -m installer --destdir="$pkgdir" dist/*.whl

    # Install .page files
    install -d "$pkgdir/usr/share/plasma-systemmonitor"
    install -Dm644 *.page -t "$pkgdir/usr/share/plasma-systemmonitor"
}
