package main

import (
	"encoding/json"
	"fmt"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// SmartContract base
type SmartContract struct {
	contractapi.Contract
}

// Basic key-value structure
type Asset struct {
	Key   string `json:"Key"`
	Value string `json:"Value"`
}

// EHR record structure (CID from IPFS stored here)
type EHRRecord struct {
	EHRID     string `json:"ehr_id"`
	PatientID string `json:"patient_id"`
	DoctorID  string `json:"doctor_id"`
	CID       string `json:"cid"`
	Type      string `json:"type"`
	CreatedAt string `json:"created_at"`
}

// InitLedger loads sample data
func (s *SmartContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
	initialAssets := []Asset{
		{Key: "test1", Value: "hello"},
		{Key: "test2", Value: "world"},
	}

	for _, asset := range initialAssets {
		assetJSON, err := json.Marshal(asset)
		if err != nil {
			return fmt.Errorf("failed to marshal: %v", err)
		}

		err = ctx.GetStub().PutState(asset.Key, assetJSON)
		if err != nil {
			return fmt.Errorf("failed to put asset %s: %v", asset.Key, err)
		}
	}
	return nil
}

// Asset management functions
func (s *SmartContract) CreateAsset(ctx contractapi.TransactionContextInterface, key string, value string) error {
	exists, err := s.AssetExists(ctx, key)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("asset %s already exists", key)
	}

	asset := Asset{Key: key, Value: value}
	assetJSON, err := json.Marshal(asset)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(key, assetJSON)
}

func (s *SmartContract) ReadAsset(ctx contractapi.TransactionContextInterface, key string) (*Asset, error) {
	data, err := ctx.GetStub().GetState(key)
	if err != nil {
		return nil, fmt.Errorf("failed to read asset %s: %v", key, err)
	}
	if data == nil {
		return nil, fmt.Errorf("asset %s not found", key)
	}

	var asset Asset
	if err := json.Unmarshal(data, &asset); err != nil {
		return nil, err
	}
	return &asset, nil
}

func (s *SmartContract) UpdateAsset(ctx contractapi.TransactionContextInterface, key string, newValue string) error {
	exists, err := s.AssetExists(ctx, key)
	if err != nil {
		return err
	}
	if !exists {
		return fmt.Errorf("asset %s does not exist", key)
	}

	asset := Asset{Key: key, Value: newValue}
	assetJSON, err := json.Marshal(asset)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(key, assetJSON)
}

func (s *SmartContract) DeleteAsset(ctx contractapi.TransactionContextInterface, key string) error {
	exists, err := s.AssetExists(ctx, key)
	if err != nil {
		return err
	}
	if !exists {
		return fmt.Errorf("asset %s does not exist", key)
	}

	return ctx.GetStub().DelState(key)
}

func (s *SmartContract) AssetExists(ctx contractapi.TransactionContextInterface, key string) (bool, error) {
	data, err := ctx.GetStub().GetState(key)
	if err != nil {
		return false, err
	}
	return data != nil, nil
}

// 🆕 Create a new EHR record and store CID from IPFS
func (s *SmartContract) CreateEHRRecord(ctx contractapi.TransactionContextInterface, ehrID, patientID, doctorID, cid, ehrType, createdAt string) error {
	ehr := EHRRecord{
		EHRID:     ehrID,
		PatientID: patientID,
		DoctorID:  doctorID,
		CID:       cid,
		Type:      ehrType,
		CreatedAt: createdAt,
	}

	ehrJSON, err := json.Marshal(ehr)
	if err != nil {
		return fmt.Errorf("failed to marshal EHRRecord: %v", err)
	}

	return ctx.GetStub().PutState(ehrID, ehrJSON)
}

// 🆕 Read an EHR record by ID
func (s *SmartContract) ReadEHRRecord(ctx contractapi.TransactionContextInterface, ehrID string) (*EHRRecord, error) {
	data, err := ctx.GetStub().GetState(ehrID)
	if err != nil {
		return nil, fmt.Errorf("failed to read EHR %s: %v", ehrID, err)
	}
	if data == nil {
		return nil, fmt.Errorf("EHR %s not found", ehrID)
	}

	var record EHRRecord
	if err := json.Unmarshal(data, &record); err != nil {
		return nil, err
	}
	return &record, nil
}

// Entry point
func main() {
	chaincode, err := contractapi.NewChaincode(new(SmartContract))
	if err != nil {
		panic(fmt.Sprintf("failed to create chaincode: %v", err))
	}

	if err := chaincode.Start(); err != nil {
		panic(fmt.Sprintf("failed to start chaincode: %v", err))
	}
}
