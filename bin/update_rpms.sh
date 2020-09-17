function print_check() {
	echo -e " \e[32m\xE2\x9C\x93 ${1}\e[0m"
}

function print_ecks() {
	echo -e " \e[31m\xE2\x9C\x97 ${1}\e[0m"
}

function update_rpms() {
	# Requirements: jq, curl

	#set -x

	# Path to download the RPMs
	FMT_STORE_DIR="${HOME}/Packages/%s"
	FMT_STORE_DIR="/mnt/largevol/venus/Packages/%s"

	FMT_RELEASES_URL="https://api.github.com/repos/%s/releases/latest"
	FMT_GH_DL_URL="https://github.com/%s/releases/download/v%s/%s"

	# I'm running bitcoin-core in a non-standard path; I hope to move this 
	# to /opt or somewhere standard
	BITCOIN_BIN_PATH="/mnt/largevol/venus/Downloads/2020/bitcoin-core-0.20.1/bitcoin-0.20.1"

	declare -A RPM_VER GITHUB_REPO FMT_DOWNLOAD_FILENAME FMT_URL_SUFFIX FMT_URL
	RPM_VER[atom]=$(atom -v | grep Atom | egrep -o '[0-9].+')
	RPM_VER[bitcoin]=$(${BITCOIN_BIN_PATH}/bin/bitcoin-cli -version | egrep -o '[0-9].+')
	RPM_VER[bisq]=$(/opt/Bisq/Bisq --help | head -1 | egrep -o '[0-9].+')
	RPM_VER[gh]=$(gh --version 2> /dev/null | head -1 | egrep -o '[0-9].+ ' | tr -d ' ')

	#set +x
	#return 1

	# Project name (as it appears on GitHub)
	GITHUB_REPO[atom]="atom/atom"
	GITHUB_REPO[bitcoin]="bitcoin/bitcoin"
	GITHUB_REPO[bisq]="bisq-network/bisq"
	GITHUB_REPO[gh]="cli/cli"

	# Atom does not include the version number in the filename of the downloaded
	# file
	FMT_DOWNLOAD_FILENAME[atom]="atom-%s.x86_64.rpm"

	# If we know the format of the filename, and the `.*\.rpm` pattern may match
	# multiple files, let's just specify the format of the filename
  FMT_URL_SUFFIX[bisq]="Bisq-64bit-%s.rpm"
  FMT_URL_SUFFIX[gh]="gh_%s_linux_amd64.rpm"

	# Bitcoin Core does not publish compiled tarballs on their GitHub project page
	FMT_URL[bitcoin]="https://bitcoincore.org/bin/bitcoin-core-%s/bitcoin-%s-x86_64-linux-gnu.tar.gz"

	for ware in "${!RPM_VER[@]}"
	do
		DOWNLOAD_DIR=$(printf "$FMT_STORE_DIR" "${ware}")
    mkdir -p "${DOWNLOAD_DIR}"

    CURR_VER="${RPM_VER[${ware}]/ /}" # Remove spaces

		DL_URL=$(printf "$FMT_GH_DL_URL" "${GITHUB_REPO[$ware]}" "%s" "%s")

		RELEASES_URL=$(printf "$FMT_RELEASES_URL" "${GITHUB_REPO[$ware]}")

		LATEST_REL=$(/usr/bin/curl -s ${RELEASES_URL})
		VER=$(echo "$LATEST_REL" | jq -r '.tag_name')
    VER=${VER#v}

		if [ -v FMT_URL[$ware] ]
		then
		  DL_URL="${FMT_URL[$ware]//\%s/$VER}"
		else
		  if [ -v FMT_URL_SUFFIX[$ware] ]
		  then
		    SUFFIX=$(printf "${FMT_URL_SUFFIX[$ware]}" "$VER")
		  else
		    SUFFIX=$(echo "$LATEST_REL" | jq -r '.assets[].name|select(match("\\.rpm$"))')
      fi

		  #printf "VER: %s\n" "$VER"
		  #printf "SUFFIX: %s\n" "$SUFFIX"
		  DL_URL=$(printf "$DL_URL" "$VER" "$SUFFIX")
		fi


    if [[ "${CURR_VER}" != "${VER}" ]]
    then
      echo "${CURR_VER} != ${VER}"
      echo "Downloading ${ware} ${VER}"

			#echo "${DL_URL}"
			#echo "${DOWNLOAD_DIR}"

			if [ -v FMT_DOWNLOAD_FILENAME[$ware] ]
			then
			  DOWNLOAD_FILENAME=$(printf "${FMT_DOWNLOAD_FILENAME[$ware]}" "$VER")
			  (cd ${DOWNLOAD_DIR} && curl -sLo ${DOWNLOAD_FILENAME} ${DL_URL})
		  else
			  (cd ${DOWNLOAD_DIR} && curl -sLJO ${DL_URL})
			fi

  		print_ecks "${ware} needs update"

    else
  		print_check "${ware} is up-to-date"
    fi

	done
	return
}

# vim: set ts=2 sw=2 tw=0 noet :
