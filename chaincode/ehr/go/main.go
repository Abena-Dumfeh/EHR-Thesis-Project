package main

import (
	"encoding/json"
	"fmt"

	"strings"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type SmartContract struct {
	contractapi.Contract
}

type EHRRecord struct {
	EHRID        string    `json:"ehr_id"`
	PatientID    string    `json:"patient_id"`
	DoctorID     string    `json:"doctor_id"`
	RecordType   string    `json:"record_type"`
	IPFSCID      string    `json:"ipfs_cid"`
	CKKSCID      string    `json:"ckks_cid,omitempty"`
	FHIRCID      string    `json:"fhir_cid,omitempty"`
	FHIREncCID   string    `json:"fhir_enc_cid,omitempty"`
	ConsentGiven bool      `json:"consent_given,omitempty"`
	CreatedAt    time.Time `json:"created_at"`
	CreatedBy    string    `json:"created_by"`
}

type Consent struct {
	EHRID      string    `json:"ehr_id"`
	FromDoctor string    `json:"from_doctor"`
	ToDoctor   string    `json:"to_doctor"`
	PatientID  string    `json:"patient_id"`
	Granted    bool      `json:"granted"`
	GrantedAt  time.Time `json:"granted_at"`
	RevokedAt  time.Time `json:"revoked_at,omitempty"`
}

type AuditLog struct {
	Action    string    `json:"action"` // "read", "update", "grant", etc.
	EHRID     string    `json:"ehr_id"`
	Invoker   string    `json:"invoker"`
	Timestamp time.Time `json:"timestamp"`
}

const (
	RoleDoctor  = "doctor"
	RoleAdmin   = "admin"
	RolePatient = "patient"
)

/*
func (s *SmartContract) CreateEHRRecord(ctx contractapi.TransactionContextInterface, ehrID, patientID, recordType, ipfsCID, ckksCID, fhirCID, fhirEncCID, consent string) error {
	ehr := map[string]string{
		"ehr_id":       ehrID,
		"patient_id":   patientID,
		"record_type":  recordType,
		"ipfs_cid":     ipfsCID,
		"ckks_cid":     ckksCID,
		"fhir_cid":     fhirCID,
		"fhir_enc_cid": fhirEncCID,
		"consent":      consent,
	}
	ehrJSON, err := json.Marshal(ehr)
	if err != nil {
		return err
	}
	return ctx.GetStub().PutState(ehrID, ehrJSON)
}*/

func (s *SmartContract) CreateEHRRecord(ctx contractapi.TransactionContextInterface,
	ehrID, patientID, doctorID, recordType, ipfsCID, ckksCID, fhirCID, fhirEncCID, createdAt string, consentGiven bool) error {

	creator, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return fmt.Errorf("failed to get client identity: %v", err)
	}

	parsedTime, err := time.Parse(time.RFC3339, createdAt)
	if err != nil {
		return fmt.Errorf("invalid createdAt timestamp format. Use RFC3339: %v", err)
	}

	ehr := EHRRecord{
		EHRID:        ehrID,
		PatientID:    patientID,
		DoctorID:     doctorID,
		RecordType:   recordType,
		IPFSCID:      ipfsCID,
		CKKSCID:      ckksCID,
		FHIRCID:      fhirCID,
		FHIREncCID:   fhirEncCID,
		ConsentGiven: consentGiven,
		CreatedAt:    parsedTime,
		CreatedBy:    creator,
	}

	ehrJSON, err := json.Marshal(ehr)
	if err != nil {
		return fmt.Errorf("failed to marshal EHRRecord: %v", err)
	}

	return ctx.GetStub().PutState(ehrID, ehrJSON)
}

/*
func (s *SmartContract) ReadEHRRecord(ctx contractapi.TransactionContextInterface, ehrID string) (string, error) {
	ehrBytes, err := ctx.GetStub().GetState(ehrID)
	if err != nil {
		return "", fmt.Errorf("failed to read EHR record: %v", err)
	}
	if ehrBytes == nil {
		return "", fmt.Errorf("EHR record with ID %s does not exist", ehrID)
	}
	return string(ehrBytes), nil
}
*/

func (s *SmartContract) ReadEHRRecord(ctx contractapi.TransactionContextInterface, ehrID string) (string, error) {
	ehrBytes, err := ctx.GetStub().GetState(ehrID)
	if err != nil {
		return "", fmt.Errorf("failed to read EHR record: %v", err)
	}
	if ehrBytes == nil {
		return "", fmt.Errorf("EHR record with ID %s does not exist", ehrID)
	}

	// Get invoker's MSP ID
	mspID, err := ctx.GetClientIdentity().GetMSPID()
	if err != nil {
		return "", fmt.Errorf("failed to get invoker MSP ID: %v", err)
	}

	// Allow AdminOrgHospital1MSP to always read
	if mspID == "AdminOrgHospital1MSP" {
		return string(ehrBytes), nil
	}

	// Parse EHR to check PatientID
	var ehr EHRRecord
	if err := json.Unmarshal(ehrBytes, &ehr); err != nil {
		return "", fmt.Errorf("failed to unmarshal EHR: %v", err)
	}

	// Check if invoker is the patient who owns the record
	invokerID, _ := ctx.GetClientIdentity().GetID()
	if strings.Contains(invokerID, ehr.PatientID) {
		return string(ehrBytes), nil
	}

	// Check if consent exists for this doctor
	consentKey := "consent_" + ehrID + "_" + mspID
	consentBytes, err := ctx.GetStub().GetState(consentKey)
	if err != nil || consentBytes == nil {
		return "", fmt.Errorf("no active consent found for EHR %s and doctor %s", ehrID, mspID)
	}

	var consent Consent
	if err := json.Unmarshal(consentBytes, &consent); err != nil {
		return "", fmt.Errorf("failed to unmarshal consent: %v", err)
	}

	if !consent.Granted {
		return "", fmt.Errorf("access to EHR %s is revoked for doctor %s", ehrID, mspID)
	}

	return string(ehrBytes), nil
}

func (s *SmartContract) EHRExists(ctx contractapi.TransactionContextInterface, ehrID string) (bool, error) {
	ehrBytes, err := ctx.GetStub().GetState(ehrID)
	if err != nil {
		return false, fmt.Errorf("failed to read EHR: %v", err)
	}
	return ehrBytes != nil, nil
}

func (s *SmartContract) ListAllEHRRecords(ctx contractapi.TransactionContextInterface) ([]string, error) {
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, fmt.Errorf("failed to get state range: %v", err)
	}
	defer resultsIterator.Close()

	var keys []string
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}
		keys = append(keys, queryResponse.Key)
	}
	return keys, nil
}

func (s *SmartContract) GrantConsent(ctx contractapi.TransactionContextInterface, ehrID, fromDoctor, toDoctor, patientID string) error {
	consent := Consent{
		EHRID:      ehrID,
		FromDoctor: fromDoctor,
		ToDoctor:   toDoctor,
		PatientID:  patientID,
		Granted:    true,
		GrantedAt:  time.Now(),
	}
	consentJSON, err := json.Marshal(consent)
	if err != nil {
		return fmt.Errorf("failed to marshal consent: %v", err)
	}
	key := "consent_" + ehrID + "_" + toDoctor
	return ctx.GetStub().PutState(key, consentJSON)
}

func (s *SmartContract) CheckConsent(ctx contractapi.TransactionContextInterface, ehrID, doctorMSP string) (bool, error) {
	key := "consent_" + ehrID + "_" + doctorMSP
	consentBytes, err := ctx.GetStub().GetState(key)
	if err != nil {
		return false, fmt.Errorf("failed to read consent state: %v", err)
	}
	if consentBytes == nil {
		return false, nil // No consent found
	}

	var consent Consent
	if err := json.Unmarshal(consentBytes, &consent); err != nil {
		return false, fmt.Errorf("failed to unmarshal consent: %v", err)
	}

	return consent.Granted, nil
}

func (s *SmartContract) ReadConsent(ctx contractapi.TransactionContextInterface, ehrID, doctorMSP string) (string, error) {
	key := "consent_" + ehrID + "_" + doctorMSP
	consentBytes, err := ctx.GetStub().GetState(key)
	if err != nil {
		return "", fmt.Errorf("failed to read consent state: %v", err)
	}
	if consentBytes == nil {
		return "", fmt.Errorf("no consent found for EHR %s and doctor %s", ehrID, doctorMSP)
	}

	return string(consentBytes), nil
}

func (s *SmartContract) RevokeConsent(ctx contractapi.TransactionContextInterface, ehrID, doctorMSP string) error {
	key := "consent_" + ehrID + "_" + doctorMSP

	consentBytes, err := ctx.GetStub().GetState(key)
	if err != nil {
		return fmt.Errorf("failed to read consent state: %v", err)
	}
	if consentBytes == nil {
		return fmt.Errorf("no existing consent to revoke for EHR %s and doctor %s", ehrID, doctorMSP)
	}

	var consent Consent
	if err := json.Unmarshal(consentBytes, &consent); err != nil {
		return fmt.Errorf("failed to unmarshal consent: %v", err)
	}

	consent.Granted = false
	consent.RevokedAt = time.Now()

	updatedBytes, err := json.Marshal(consent)
	if err != nil {
		return fmt.Errorf("failed to marshal updated consent: %v", err)
	}

	return ctx.GetStub().PutState(key, updatedBytes)
}

func (s *SmartContract) ListConsentLogs(ctx contractapi.TransactionContextInterface, ehrID string) ([]Consent, error) {
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, fmt.Errorf("failed to get state range: %v", err)
	}
	defer resultsIterator.Close()

	var consents []Consent

	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		if strings.HasPrefix(queryResponse.Key, "consent_"+ehrID+"_") {
			var consent Consent
			if err := json.Unmarshal(queryResponse.Value, &consent); err != nil {
				continue // skip invalid records
			}
			consents = append(consents, consent)
		}
	}
	return consents, nil
}

func (s *SmartContract) LogAudit(ctx contractapi.TransactionContextInterface, action, ehrID string) error {
	invoker, _ := ctx.GetClientIdentity().GetID()
	log := AuditLog{
		Action:    action,
		EHRID:     ehrID,
		Invoker:   invoker,
		Timestamp: time.Now(),
	}
	logJSON, _ := json.Marshal(log)
	key := "audit_" + ehrID + "_" + fmt.Sprint(time.Now().UnixNano())
	return ctx.GetStub().PutState(key, logJSON)
}

// =======================
// PATIENT-SPECIFIC FUNCTIONS
// =======================

// Helper function to verify patient identity
func (s *SmartContract) verifyPatientIdentity(ctx contractapi.TransactionContextInterface, patientID string) error {
	invokerID, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return fmt.Errorf("failed to get invoker identity: %v", err)
	}

	mspID, err := ctx.GetClientIdentity().GetMSPID()
	if err != nil {
		return fmt.Errorf("failed to get MSP ID: %v", err)
	}

	// Only patients from PatientOrg can call patient functions
	if mspID != "PatientOrgHospital1MSP" {
		return fmt.Errorf("only patients can call this function")
	}

	// Verify the invoker is the patient in question
	if !strings.Contains(invokerID, patientID) {
		return fmt.Errorf("access denied: you can only manage your own records")
	}

	return nil
}

// PatientGrantConsent - Patient grants access to a specific doctor for a specific EHR record
func (s *SmartContract) PatientGrantConsent(ctx contractapi.TransactionContextInterface, ehrID, doctorMSP, doctorID string) error {
	// Get patient ID from the EHR record
	ehrBytes, err := ctx.GetStub().GetState(ehrID)
	if err != nil {
		return fmt.Errorf("failed to read EHR record: %v", err)
	}
	if ehrBytes == nil {
		return fmt.Errorf("EHR record with ID %s does not exist", ehrID)
	}

	var ehr EHRRecord
	if err := json.Unmarshal(ehrBytes, &ehr); err != nil {
		return fmt.Errorf("failed to unmarshal EHR: %v", err)
	}

	// Verify patient identity
	if err := s.verifyPatientIdentity(ctx, ehr.PatientID); err != nil {
		return err
	}

	// Create consent record
	consent := Consent{
		EHRID:      ehrID,
		FromDoctor: "PATIENT_INITIATED", // Indicate this was patient-initiated
		ToDoctor:   doctorMSP,
		PatientID:  ehr.PatientID,
		Granted:    true,
		GrantedAt:  time.Now(),
	}

	consentJSON, err := json.Marshal(consent)
	if err != nil {
		return fmt.Errorf("failed to marshal consent: %v", err)
	}

	key := "consent_" + ehrID + "_" + doctorMSP
	if err := ctx.GetStub().PutState(key, consentJSON); err != nil {
		return fmt.Errorf("failed to store consent: %v", err)
	}

	// Log the consent grant
	s.LogAudit(ctx, "patient_grant_consent", ehrID)

	return nil
}

// PatientRevokeConsent - Patient revokes doctor access to their EHR record
func (s *SmartContract) PatientRevokeConsent(ctx contractapi.TransactionContextInterface, ehrID, doctorMSP string) error {
	// Get patient ID from the EHR record
	ehrBytes, err := ctx.GetStub().GetState(ehrID)
	if err != nil {
		return fmt.Errorf("failed to read EHR record: %v", err)
	}
	if ehrBytes == nil {
		return fmt.Errorf("EHR record with ID %s does not exist", ehrID)
	}

	var ehr EHRRecord
	if err := json.Unmarshal(ehrBytes, &ehr); err != nil {
		return fmt.Errorf("failed to unmarshal EHR: %v", err)
	}

	// Verify patient identity
	if err := s.verifyPatientIdentity(ctx, ehr.PatientID); err != nil {
		return err
	}

	// Revoke consent
	key := "consent_" + ehrID + "_" + doctorMSP
	consentBytes, err := ctx.GetStub().GetState(key)
	if err != nil {
		return fmt.Errorf("failed to read consent state: %v", err)
	}
	if consentBytes == nil {
		return fmt.Errorf("no existing consent to revoke for EHR %s and doctor %s", ehrID, doctorMSP)
	}

	var consent Consent
	if err := json.Unmarshal(consentBytes, &consent); err != nil {
		return fmt.Errorf("failed to unmarshal consent: %v", err)
	}

	consent.Granted = false
	consent.RevokedAt = time.Now()

	updatedBytes, err := json.Marshal(consent)
	if err != nil {
		return fmt.Errorf("failed to marshal updated consent: %v", err)
	}

	if err := ctx.GetStub().PutState(key, updatedBytes); err != nil {
		return fmt.Errorf("failed to update consent: %v", err)
	}

	// Log the consent revocation
	s.LogAudit(ctx, "patient_revoke_consent", ehrID)

	return nil
}

// PatientListMyRecords - Patient lists all their own EHR records
func (s *SmartContract) PatientListMyRecords(ctx contractapi.TransactionContextInterface, patientID string) ([]EHRRecord, error) {
	// Verify patient identity
	if err := s.verifyPatientIdentity(ctx, patientID); err != nil {
		return nil, err
	}

	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, fmt.Errorf("failed to get state range: %v", err)
	}
	defer resultsIterator.Close()

	var patientRecords []EHRRecord

	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		// Skip non-EHR records (consent, audit logs, etc.)
		if strings.HasPrefix(queryResponse.Key, "consent_") ||
			strings.HasPrefix(queryResponse.Key, "audit_") {
			continue
		}

		var ehr EHRRecord
		if err := json.Unmarshal(queryResponse.Value, &ehr); err != nil {
			continue // Skip invalid records
		}

		// Only include records belonging to this patient
		if ehr.PatientID == patientID {
			patientRecords = append(patientRecords, ehr)
		}
	}

	// Log the access
	s.LogAudit(ctx, "patient_list_my_records", "BULK_ACCESS")

	return patientRecords, nil
}

// PatientViewMyConsentLog - Patient views all consent activities for their records
func (s *SmartContract) PatientViewMyConsentLog(ctx contractapi.TransactionContextInterface, patientID string) ([]Consent, error) {
	// Verify patient identity
	if err := s.verifyPatientIdentity(ctx, patientID); err != nil {
		return nil, err
	}

	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, fmt.Errorf("failed to get state range: %v", err)
	}
	defer resultsIterator.Close()

	var patientConsents []Consent

	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		// Only process consent records
		if !strings.HasPrefix(queryResponse.Key, "consent_") {
			continue
		}

		var consent Consent
		if err := json.Unmarshal(queryResponse.Value, &consent); err != nil {
			continue // Skip invalid records
		}

		// Only include consents for this patient
		if consent.PatientID == patientID {
			patientConsents = append(patientConsents, consent)
		}
	}

	// Log the access
	s.LogAudit(ctx, "patient_view_consent_log", "BULK_ACCESS")

	return patientConsents, nil
}

// PatientViewMyAuditLog - Patient views audit log for their records
func (s *SmartContract) PatientViewMyAuditLog(ctx contractapi.TransactionContextInterface, patientID string) ([]AuditLog, error) {
	// Verify patient identity
	if err := s.verifyPatientIdentity(ctx, patientID); err != nil {
		return nil, err
	}

	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, fmt.Errorf("failed to get state range: %v", err)
	}
	defer resultsIterator.Close()

	var patientAudits []AuditLog

	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		// Only process audit records
		if !strings.HasPrefix(queryResponse.Key, "audit_") {
			continue
		}

		var audit AuditLog
		if err := json.Unmarshal(queryResponse.Value, &audit); err != nil {
			continue // Skip invalid records
		}

		// Check if this audit is for any of patient's records
		if strings.Contains(audit.EHRID, patientID) || audit.EHRID == "BULK_ACCESS" {
			patientAudits = append(patientAudits, audit)
		}
	}

	return patientAudits, nil
}

// PatientCreateEHRRecord - Patient creates their own EHR record
func (s *SmartContract) PatientCreateEHRRecord(ctx contractapi.TransactionContextInterface,
	ehrID, patientID, recordType, ipfsCID, ckksCID, fhirCID, fhirEncCID string) error {

	// Verify patient identity
	if err := s.verifyPatientIdentity(ctx, patientID); err != nil {
		return err
	}

	// Check if EHR already exists
	exists, err := s.EHRExists(ctx, ehrID)
	if err != nil {
		return fmt.Errorf("failed to check EHR existence: %v", err)
	}
	if exists {
		return fmt.Errorf("EHR record with ID %s already exists", ehrID)
	}

	creator, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return fmt.Errorf("failed to get client identity: %v", err)
	}

	ehr := EHRRecord{
		EHRID:        ehrID,
		PatientID:    patientID,
		DoctorID:     "", // Patient-created, no doctor initially
		RecordType:   recordType,
		IPFSCID:      ipfsCID,
		CKKSCID:      ckksCID,
		FHIRCID:      fhirCID,
		FHIREncCID:   fhirEncCID,
		ConsentGiven: false, // No initial consent
		CreatedAt:    time.Now(),
		CreatedBy:    creator,
	}

	ehrJSON, err := json.Marshal(ehr)
	if err != nil {
		return fmt.Errorf("failed to marshal EHRRecord: %v", err)
	}

	if err := ctx.GetStub().PutState(ehrID, ehrJSON); err != nil {
		return fmt.Errorf("failed to store EHR record: %v", err)
	}

	// Log the creation
	s.LogAudit(ctx, "patient_create_record", ehrID)

	return nil
}

// PatientGetConsentStatus - Patient checks consent status for a specific record and doctor
func (s *SmartContract) PatientGetConsentStatus(ctx contractapi.TransactionContextInterface, ehrID, doctorMSP string) (*Consent, error) {
	// Get patient ID from the EHR record
	ehrBytes, err := ctx.GetStub().GetState(ehrID)
	if err != nil {
		return nil, fmt.Errorf("failed to read EHR record: %v", err)
	}
	if ehrBytes == nil {
		return nil, fmt.Errorf("EHR record with ID %s does not exist", ehrID)
	}

	var ehr EHRRecord
	if err := json.Unmarshal(ehrBytes, &ehr); err != nil {
		return nil, fmt.Errorf("failed to unmarshal EHR: %v", err)
	}

	// Verify patient identity
	if err := s.verifyPatientIdentity(ctx, ehr.PatientID); err != nil {
		return nil, err
	}

	// Get consent status
	key := "consent_" + ehrID + "_" + doctorMSP
	consentBytes, err := ctx.GetStub().GetState(key)
	if err != nil {
		return nil, fmt.Errorf("failed to read consent state: %v", err)
	}
	if consentBytes == nil {
		return nil, fmt.Errorf("no consent record found for EHR %s and doctor %s", ehrID, doctorMSP)
	}

	var consent Consent
	if err := json.Unmarshal(consentBytes, &consent); err != nil {
		return nil, fmt.Errorf("failed to unmarshal consent: %v", err)
	}

	return &consent, nil
}

// PatientBulkGrantConsent - Patient grants consent to multiple doctors for a specific record
func (s *SmartContract) PatientBulkGrantConsent(ctx contractapi.TransactionContextInterface, ehrID string, doctorMSPs []string) error {
	// Get patient ID from the EHR record
	ehrBytes, err := ctx.GetStub().GetState(ehrID)
	if err != nil {
		return fmt.Errorf("failed to read EHR record: %v", err)
	}
	if ehrBytes == nil {
		return fmt.Errorf("EHR record with ID %s does not exist", ehrID)
	}

	var ehr EHRRecord
	if err := json.Unmarshal(ehrBytes, &ehr); err != nil {
		return fmt.Errorf("failed to unmarshal EHR: %v", err)
	}

	// Verify patient identity
	if err := s.verifyPatientIdentity(ctx, ehr.PatientID); err != nil {
		return err
	}

	// Grant consent to each doctor
	for _, doctorMSP := range doctorMSPs {
		consent := Consent{
			EHRID:      ehrID,
			FromDoctor: "PATIENT_BULK_GRANT",
			ToDoctor:   doctorMSP,
			PatientID:  ehr.PatientID,
			Granted:    true,
			GrantedAt:  time.Now(),
		}

		consentJSON, err := json.Marshal(consent)
		if err != nil {
			return fmt.Errorf("failed to marshal consent for doctor %s: %v", doctorMSP, err)
		}

		key := "consent_" + ehrID + "_" + doctorMSP
		if err := ctx.GetStub().PutState(key, consentJSON); err != nil {
			return fmt.Errorf("failed to store consent for doctor %s: %v", doctorMSP, err)
		}
	}

	// Log the bulk consent
	s.LogAudit(ctx, "patient_bulk_grant_consent", ehrID)

	return nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(new(SmartContract))
	if err != nil {
		fmt.Printf("Error creating EHR chaincode: %v\n", err)
		return
	}

	if err := chaincode.Start(); err != nil {
		fmt.Printf("Error starting EHR chaincode: %v\n", err)
	}
}
