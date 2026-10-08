#!/usr/bin/env bash
# ==============================================================================
# GeneWeave-Risk: 1000 Genomes Phase 3 Data Acquisition & Regional Extraction
# Target genes: DPYD (Chr 1), CYP2C9/CYP2C19 (Chr 10), SLCO1B1 (Chr 12), CYP2D6 (Chr 22)
# Reference: GRCh37 / hg19 (1000 Genomes Phase 3 Release 20130502)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

RAW_DIR="${PROJECT_ROOT}/data/raw/1000genomes_phase3_grch37"
META_DIR="${PROJECT_ROOT}/data/metadata"
REGIONS_DIR="${PROJECT_ROOT}/data/regions"
RESEARCH_DIR="${PROJECT_ROOT}/research"

BASE_URL="http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502"

mkdir -p "${RAW_DIR}" "${META_DIR}" "${REGIONS_DIR}" "${RESEARCH_DIR}"

echo "======================================================================"
echo "1. Downloading 1000 Genomes Phase 3 Metadata & Chromosome VCFs"
echo "======================================================================"

download_and_verify() {
    local url="$1"
    local dest="$2"
    
    if [ -f "${dest}" ]; then
        if [[ "${dest}" == *.gz ]]; then
            if gzip -t "${dest}" 2>/dev/null; then
                echo "File verified valid gzip: ${dest}"
                return 0
            else
                echo "Corrupt gzip detected for ${dest}, removing and redownloading..."
                rm -f "${dest}" "${dest}.aria2"
            fi
        else
            echo "File exists: ${dest}"
            return 0
        fi
    fi

    echo "Downloading ${url} -> ${dest}..."
    if command -v aria2c &> /dev/null; then
        aria2c -x 4 -s 4 --file-allocation=trunc --continue=true --dir="$(dirname "${dest}")" --out="$(basename "${dest}")" "${url}" || curl -f -L -C - "${url}" -o "${dest}"
    else
        curl -f -L -C - "${url}" -o "${dest}"
    fi

    if [[ "${dest}" == *.gz ]]; then
        echo "Verifying gzip integrity of ${dest}..."
        if ! gzip -t "${dest}" 2>/dev/null; then
            echo "Aria2 download failed gzip integrity check for ${dest}, falling back to clean curl download..."
            rm -f "${dest}" "${dest}.aria2"
            curl -f -L "${url}" -o "${dest}"
            gzip -t "${dest}"
        fi
        echo "Gzip verification PASSED for ${dest}"
    fi
}

# Download sample panel
PANEL_FILE="${META_DIR}/integrated_call_samples_v3.20130502.ALL.panel"
download_and_verify "${BASE_URL}/integrated_call_samples_v3.20130502.ALL.panel" "${PANEL_FILE}"

# Chromosome VCF files to download
CHRS=("1" "10" "12" "22")

for CHR in "${CHRS[@]}"; do
    VCF_NAME="ALL.chr${CHR}.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz"
    TBI_NAME="${VCF_NAME}.tbi"
    
    VCF_PATH="${RAW_DIR}/${VCF_NAME}"
    TBI_PATH="${RAW_DIR}/${TBI_NAME}"
    
    download_and_verify "${BASE_URL}/${VCF_NAME}" "${VCF_PATH}"
    download_and_verify "${BASE_URL}/${TBI_NAME}" "${TBI_PATH}"
done

echo "======================================================================"
echo "2. Validating Downloaded VCF Integrity & Headers"
echo "======================================================================"

for CHR in "${CHRS[@]}"; do
    VCF_NAME="ALL.chr${CHR}.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz"
    VCF_PATH="${RAW_DIR}/${VCF_NAME}"

    if [ -f "${VCF_PATH}" ] && gzip -t "${VCF_PATH}" 2>/dev/null; then
        echo "Testing gzip integrity for Chr ${CHR}..."
        gzip -t "${VCF_PATH}"
        
        echo "Verifying VCF header readability with bcftools..."
        bcftools view -h "${VCF_PATH}" | head -n 20 > /dev/null
    fi
done

echo "======================================================================"
echo "3. Extracting Target Pharmacogene Regions"
echo "======================================================================"

# Coordinates verified via Ensembl GRCh37 REST API lookup
# DPYD: Chr 1: 97543299-98386605
# CYP2C19 & CYP2C9: Chr 10: 96447911-96749147 (Combined region spanning CYP2C19 start to CYP2C9 end)
# SLCO1B1: Chr 12: 21284136-21392180
# CYP2D6: Chr 22: 42522501-42526908

extract_region() {
    local chr="$1"
    local region="$2"
    local output_name="$3"
    local raw_vcf="${RAW_DIR}/ALL.chr${chr}.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz"
    local remote_vcf="${BASE_URL}/ALL.chr${chr}.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz"
    local out_vcf="${REGIONS_DIR}/${output_name}"

    local source_vcf="${remote_vcf}"
    if [ -f "${raw_vcf}" ] && gzip -t "${raw_vcf}" 2>/dev/null; then
        source_vcf="${raw_vcf}"
        echo "Extracting region ${region} from local Chr ${chr} VCF into ${output_name}..."
    else
        echo "Extracting region ${region} directly from remote Chr ${chr} VCF URL into ${output_name}..."
    fi

    bcftools view -r "${region}" -O z -o "${out_vcf}" "${source_vcf}"
    
    echo "Indexing extracted region ${output_name}..."
    tabix -f -p vcf "${out_vcf}"
}

extract_region "1" "1:97543299-98386605" "DPYD_GRCh37.vcf.gz"
extract_region "10" "10:96447911-96749147" "CYP2C9_CYP2C19_GRCh37.vcf.gz"
extract_region "12" "12:21284136-21392180" "SLCO1B1_GRCh37.vcf.gz"
extract_region "22" "22:42522501-42526908" "CYP2D6_GRCh37.vcf.gz"

echo "======================================================================"
echo "4. Executing Dataset Audit & Report Generation"
echo "======================================================================"

python3 "${SCRIPT_DIR}/audit_1000g.py"

echo "======================================================================"
echo "Process Complete! Audit reports created:"
echo " - ${RESEARCH_DIR}/dataset_audit.json"
echo " - ${RESEARCH_DIR}/dataset_audit.md"
echo "======================================================================"
