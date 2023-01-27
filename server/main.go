package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
)

// Transaction Limit for API: 50,000 transactions

//  This Locations API gets a list of trains and their locations and where approaching.
// http://lapi.transitchicago.com/api/1.0/ttpositions.aspx?key=x&rt=red&outputType=JSON

// A struct representing the response from the CTA Locations API
type LocationsResponse struct {
	Tracker CTATransitTracker `json:"ctatt"`
}

// A struct representing the transit tracker object
type CTATransitTracker struct {
	ErrorCode string  `json:"errCd"`
	ErrorName string  `json:"errNm"`
	Route     []Route `json:"route"`
	Timestamp string  `json:"tmst"`
}

// A struct representing a route (i.e., CTA Line)
type Route struct {
	Name   string  `json:"@name"`
	Trains []Train `json:"train"`
}

// A struct representing a train on a route
type Train struct {
	ArrivalTime         string `json:"arrT"`
	DestinationName     string `json:"destNm"`
	DestinationStation  string `json:"destSt"`
	HeadingDegrees      string `json:"heading"`
	IsApproaching       string `json:"isApp"`
	IsDelayed           string `json:"isDly"`
	NextStationId       string `json:"nextStaId"`
	NextStationName     string `json:"nextStaNm"`
	NextStopId          string `json:"nextStpId"`
	TrainRouteDirection string `json:"trDr"`
}

// Custom Error. Implents error interface Error() method.
type InvalidLineError struct{}

func (ie *InvalidLineError) Error() string {
	return "Invalid Line!"
}

// FUNCTIONS
type Line int64

// Enumeration of Line
const (
	Undefined Line = iota
	Blue
	Brown
	Green
	Orange
	Pink
	Purple
	Red
	Yellow
)

// String returns the string version of the enumerated Line type.
func (l Line) String() string {
	switch l {
	case Blue:
		return "Blue"
	case Brown:
		return "Brown"
	case Green:
		return "Green"
	case Orange:
		return "Orange"
	case Pink:
		return "Pink"
	case Purple:
		return "Purple"
	case Red:
		return "Red"
	case Yellow:
		return "Yellow"
	}
	return "Undefined"
}

// getTrainLineLocations returns all the current locations of the specified line.
func getTrainLineLocations(l Line) (*LocationsResponse, error) {
	// implement return functionality and making api request below
	var req strings.Builder
	req.WriteString("http://lapi.transitchicago.com/api/1.0/ttpositions.aspx?key=")
	var apiKey string = os.Getenv("CTA_API_KEY")
	req.WriteString(apiKey)
	switch l {
	case Blue:
		req.WriteString("&rt=blue&outputType=JSON")
	case Brown:
		req.WriteString("&rt=brn&outputType=JSON")
	case Green:
		req.WriteString("&rt=g&outputType=JSON")
	case Orange:
		req.WriteString("&rt=org&outputType=JSON")
	case Pink:
		req.WriteString("&rt=pink&outputType=JSON")
	case Purple:
		req.WriteString("&rt=p&outputType=JSON")
	case Red:
		req.WriteString("&rt=red&outputType=JSON")
	case Yellow:
		req.WriteString("&rt=y&outputType=JSON")
	default:
		return nil, &InvalidLineError{}
	}

	// Get request
	res, err := http.Get(req.String())
	if err != nil {
		fmt.Print(err.Error())
		return nil, err
	}
	responseData, err := ioutil.ReadAll(res.Body)
	if err != nil {
		fmt.Print(err.Error())
		return nil, err
	}
	// Unmarshall the returned JSON string into variable
	var responseObject LocationsResponse
	json.Unmarshal(responseData, &responseObject)
	return &responseObject, nil
}

// getTrainLocationsAllLines returns the current locations of all trains across all lines
func getAllTrainLocationsAllLines() (*LocationsResponse, error) {
	// implement return functionality and making api request below
	var req strings.Builder
	req.WriteString("http://lapi.transitchicago.com/api/1.0/ttpositions.aspx?key=")
	var apiKey string = os.Getenv("CTA_API_KEY")
	req.WriteString(apiKey)
	req.WriteString("&rt=blue,brn,g,org,pink,p,red,y&outputType=JSON")

	// Get request
	res, err := http.Get(req.String())
	if err != nil {
		fmt.Print(err.Error())
		return nil, err
	}
	responseData, err := ioutil.ReadAll(res.Body)
	if err != nil {
		fmt.Print(err.Error())
		return nil, err
	}
	// Unmarshall the returned JSON string into variable
	var responseObject LocationsResponse
	json.Unmarshal(responseData, &responseObject)
	return &responseObject, nil
}

// getTrainLineLocation returns a map with Line as the key, and Train as the type.
// This map consists of train locations per line type.
func getAllTrainLocations() (map[Line][]Train, error) {
	res := make(map[Line][]Train)
	resObj, err := getAllTrainLocationsAllLines()
	if err != nil {
		return nil, err
	}

	// Expected order: blue,brn,g,org,pink,p,red,y
	res[Blue] = resObj.Tracker.Route[0].Trains
	res[Brown] = resObj.Tracker.Route[1].Trains
	res[Green] = resObj.Tracker.Route[2].Trains
	res[Orange] = resObj.Tracker.Route[3].Trains
	res[Pink] = resObj.Tracker.Route[4].Trains
	res[Purple] = resObj.Tracker.Route[5].Trains
	res[Red] = resObj.Tracker.Route[6].Trains
	res[Yellow] = resObj.Tracker.Route[7].Trains

	return res, nil
}

// getTrainLineLocation returns a map with Line as the key, and Train as the type.
// This map consists of train locations per line type only if they are approaching
// a station.
func getAllTrainLocationsArriving() (map[Line][]Train, error) {
	res := make(map[Line][]Train)
	resObj, err := getAllTrainLocationsAllLines()
	if err != nil {
		return nil, err
	}

	// Expected order: blue,brn,g,org,pink,p,red,y
	res[Blue] = resObj.Tracker.Route[0].filterOnlyApproaching()
	res[Brown] = resObj.Tracker.Route[1].filterOnlyApproaching()
	res[Green] = resObj.Tracker.Route[2].filterOnlyApproaching()
	res[Orange] = resObj.Tracker.Route[3].filterOnlyApproaching()
	res[Pink] = resObj.Tracker.Route[4].filterOnlyApproaching()
	res[Purple] = resObj.Tracker.Route[5].filterOnlyApproaching()
	res[Red] = resObj.Tracker.Route[6].filterOnlyApproaching()
	res[Yellow] = resObj.Tracker.Route[7].filterOnlyApproaching()

	return res, nil
}

// filterOnlyApproaching method returns a slice of the Train type consisting
// of trains that are arriving/approaching a station.
func (r *Route) filterOnlyApproaching() []Train {
	var ret []Train
	for _, train := range r.Trains {
		if isArriving(train) {
			ret = append(ret, train)
		}
	}
	return ret
}

// isArriving returns true if train is approaching a station, false otherwise.
func isArriving(t Train) bool {
	return t.IsApproaching == "1"
}

func main() {
	envErr := godotenv.Load()
	if envErr != nil {
		log.Fatal("Error loading .env file")
	}

	// go printPeriodically()
	startServer()
}

func startServer() {
	// Create instance of a mux Router
	router := mux.NewRouter().StrictSlash(true)
	router.HandleFunc("/trains/{line}", returnSingleLineTrains)
	router.HandleFunc("/trains", returnAllLinesTrains)
	log.Fatal(http.ListenAndServe(":8080", router))
}

func printPeriodically() {
	for {
		time.Sleep(5 * time.Second)
		fmt.Println("/-------------------------------------------------------------------/")
		trainsMap, err := getAllTrainLocationsArriving()
		if err != nil {
			fmt.Println(err.Error())
			os.Exit(1)
		}
		for key, trains := range trainsMap {
			for _, train := range trains {
				fmt.Println("[", key, "]", train.NextStationName, "[Towards", train.DestinationName, "]",
					"| Approaching:", train.IsApproaching)
			}
		}
		fmt.Println("/-------------------------------------------------------------------/")
	}
}

// REST API!
// Endpoint(s):
//   - GET /trains/:line
//     > returns trains for 'line'
//     > ?approaching={true} : filters to trains approaching at stations
func returnSingleLineTrains(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	line := vars["line"]

	// Retrieve and marshall
	lineEnum := paramToLine(line)
	responseObject, err := getTrainLineLocations(lineEnum)
	if err != nil {
		fmt.Fprintf(w, "Error retrieving train locations: %s", err)
		return
	}

	// Check if need to filter to approaching trains only based on query param
	approaching := r.URL.Query().Get("approaching")
	var lineTrains []Train
	if strings.EqualFold("true", approaching) {
		lineTrains = responseObject.Tracker.Route[0].filterOnlyApproaching()
	} else {
		lineTrains = responseObject.Tracker.Route[0].Trains
	}

	json.NewEncoder(w).Encode(lineTrains)
}

func returnAllLinesTrains(w http.ResponseWriter, r *http.Request) {
	approaching := r.URL.Query().Get("approaching")
	var trainsMap map[Line][]Train
	var err error

	if strings.EqualFold(approaching, "true") {
		trainsMap, err = getAllTrainLocationsArriving()
	} else {
		trainsMap, err = getAllTrainLocations()
	}

	if err != nil {
		fmt.Fprintf(w, "Error retrieving train locations: %s", err)
		return
	}

	// Create map with key as Line string to return in response
	var trainsStringKey = make(map[string][]Train)
	for key, trains := range trainsMap {
		trainsStringKey[key.String()] = trains
	}

	json.NewEncoder(w).Encode(trainsStringKey)
}

func paramToLine(s string) Line {
	var l Line
	switch {
	case s == "blue":
		l = Blue
	case s == "brown":
		l = Brown
	case s == "green":
		l = Green
	case s == "orange":
		l = Orange
	case s == "pink":
		l = Pink
	case s == "purple":
		l = Purple
	case s == "red":
		l = Red
	case s == "yellow":
		l = Yellow
	default:
		l = Undefined
	}
	return l
}
