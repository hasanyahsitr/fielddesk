# Third-party notices

The FieldDesk source is distributed under [MIT](LICENSE). That license does not relicense third-party software, model weights, trademarks or downloaded content.

## Windows runtime distribution

The Windows x64 ZIP includes an existing official embedded CPython runtime and the following Python libraries. Their applicable license files are retained in the distribution; inspect them for the actual terms and transitive notices.

| Component | Included license location |
|---|---|
| CPython | `runtime/LICENSE.txt` |
| pypdf | `runtime/Lib/site-packages/pypdf-*.dist-info/` |
| Pillow and included native libraries | `runtime/Lib/site-packages/pillow-*.dist-info/` |
| pypdfium2 and PDFium | `runtime/Lib/site-packages/pypdfium2-*.dist-info/` and package license files |

Source installs resolve the supported ranges in `requirements.txt`. The runtime ZIP contains the versions present in the input runtime/package directories at build time.

## Separately obtained tools and services

Catalog programs, installers, operating-system images, model weights, llama.cpp and Tesseract are not included in FieldDesk release ZIPs. They remain subject to their publishers' licenses. A catalog listing does not establish redistribution rights, endorsement or affiliation. Commercial software may require a license; trials do not grant a permanent license.

API providers set their own access, data handling, price and quota terms. FieldDesk does not supply API credits or guarantee free access. Product names identify compatible or cataloged tools and remain their owners' marks.

FieldDesk is a working project name. Name availability, design originality and trademark registration have not been established; this release provides no such guarantee.
