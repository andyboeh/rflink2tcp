pkgname=rflink2tcp-git
pkgver=0.1
pkgrel=1
pkgdesc="Simple RFLink-ESP MQTT to TCP bridge"
arch=('any')
url="https://github.com/andyboeh/rflink2tcp"
license=('GPL')
depends=('python' 'python-paho-mqtt')
install='rflink2tcp.install'
source=('rflink2tcp-git::git+https://github.com/andyboeh/rflink2tcp.git'
        'rflink2tcp.install'
        'rflink2tcp.sysusers'
        'rflink2tcp.service')
provides=('rflink2tcp')
conflicts=('rflink2tcp')
sha256sums=('SKIP'
            'f22c24b85f20b7f3cf4f36a4ed8e6c8d4680f90d515e377c7851dd8af6f294ab'
            'e4012913a01bc70bd5a5ba900c23a7b0062c2f6b960d5649baa1b31e1ba5d0e1'
            '3a1ed60e0e31edd22ac4248579fbac30042208281eda49d6592a77b2ff0e6230')
backup=('opt/rflink2tcp/rflink2tcp.yaml')

pkgver() {
  cd "$pkgname"
  printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package() {
  cd "${pkgname}"
  install -d "${pkgdir}/opt/rflink2tcp"
  cp rflink2tcp.py "${pkgdir}/opt/rflink2tcp/rflink2tcp.py"
  cp -R pyezr "${pkgdir}/opt/rflink2tcp/"
  install -Dm644 "${srcdir}/rflink2tcp.service" "${pkgdir}/usr/lib/systemd/system/rflink2tcp.service"
  install -Dm644 "${srcdir}/rflink2tcp.sysusers" "${pkgdir}/usr/lib/sysusers.d/rflink2tcp.conf"
  install -Dm644 rflink2tcp.yaml "${pkgdir}/opt/rflink2tcp/rflink2tcp.yaml"
}
