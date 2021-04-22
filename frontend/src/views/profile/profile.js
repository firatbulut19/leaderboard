import React, { Component } from "react";
import axios from 'axios'
import { serverUrl } from '../../utils/get-url'
import { Button, Alert } from "react-bootstrap";

import "./profile.css";

export default class Profile extends Component {

  constructor(props) {
    super(props);
    this.state = {
      user_id: '',
      display_name: '',
      country: '',
      rank: 0,
      country_rank: 0,
      points: 0,
      isHiddenStates: [true, true, true, true],
      //   user_id: Cookies.get("user_id")
    }
  }

  handleChange = event => {

    event.preventDefault();
    this.setState({ [event.target.name]: event.target.value });

  }

  handleValidation() {
    let formIsValid = true;
    let new_errors = {};
    //Name
    if (this.state.display_name.length !== 0) {
      formIsValid = false;
      new_errors["display_name"] = "Display name cannot be empty.";
    }
    if (this.state.country_.length !== 0 && this.state.newpw.length < 8) {
      formIsValid = false;
      new_errors["newpw"] = "New password must be at least 8 characters.";
    }

    this.setState({ errors: new_errors });
    return formIsValid;
  }

  setHiddenStates(showNumber) {
    let tempStates = this.state.isHiddenStates;
    for (let i = 0; i < tempStates.length; i++) {
      tempStates[i] = !(i === showNumber);
    }
    this.setState({ isHiddenStates: tempStates });
  }

  handleSubmit = event => {

    const data = {
      display_name: this.state.display_name,
    }

    axios.put(serverUrl + 'user/profile/' + this.state.user_id + '/', data)
      .then(res => {
        this.setHiddenStates(0);

      }).catch((error) => {


      }

      )
  }

  componentDidMount() {
    const user_id = this.props.location.state.user_id
    axios.get(serverUrl + 'user/profile/' + user_id + '/')
      .then(res => {
        console.log("res data:  " + res.data)

        this.setState({ user_id: res.data.user_id })
        this.setState({ display_name: res.data.display_name })
        this.setState({ rank: res.data.rank })
        this.setState({ country_rank: res.data.country_rank })
        this.setState({ points: res.data.points })

      }).catch(err => {
        console.log("error:  " + err)
      })


  }


  render() {

    var countries = require("i18n-iso-countries")

    var country_code_dict = countries.getNames("en", {select: "official"});

    let country_code_list = Object.keys(country_code_dict).map((country_code) => {
      return <option value={country_code}>{country_code}</option>;
    });

    return (
      <div className='background'>
        <div className="profile-container">
          <Alert variant="success" hidden={this.state.isHiddenStates[0]}>
            Profile details updated.
            </Alert>
          <Alert variant="danger" hidden={this.state.isHiddenStates[3]}>
            Something went wrong.
            </Alert>
          <div className="justify-content-center" id="header3">
            <h2 className="text-center">Profile Page</h2>
          </div>
          <div className="profile-form row">

            <div className=" col-lg-6 col-md-6 col-sm-6 no-padding-left border-right border-left">
              <h3 className="text-center heading-2">Change Details</h3>
              <div className="account-update">
                <form className='needs-validation' onSubmit={this.handleSubmit} noValidate>
                  <div className="form-group row">
                    <label className="col-4 align-middle">User ID</label>
                    <div className="col">
                      <input type="text" name="user_id" className="form-control col" value={this.state.user_id}
                        onChange={this.handleChange} disabled />
                    </div>
                  </div>
                  <div className="form-group row">
                    <label className="col-4 align-middle">Display Name</label>
                    <div className="col">
                      <input type="text" name="display_name" className="form-control col" value={this.state.display_name}
                        onChange={this.handleChange} required />
                      <div className="error">{this.state.errors["display_name"]}</div>
                    </div>
                  </div>
                  <div className="form-group row">
                    <label className="col-4 align-middle">Country</label>
                    <div className="col">
                      <select
                        className="form-control col"
                        name="country"
                        onChange={this.handleChange}
                        required
                      >
                        <option selected disabled>
                          Please Select
                        </option>
                        {country_code_list}
                      </select>
                      <div className="error">{this.state.errors["display_name"]}</div>
                    </div>
                  </div>
                  <div className="form-group row" hidden={this.state.isCustomer}>
                    <label className="col-4 align-middle">Rank</label>
                    <div className="col">
                      <input type="text" name="rank" className="form-control col" value={this.state.rank}
                        onChange={this.handleChange} disabled />
                    </div>
                  </div>
                  <div className="form-group row">
                    <label className="col-4 align-middle">Country Rank</label>
                    <div className="col">
                      <input type="text" name="country_rank" className="form-control col" value={this.state.country_rank}
                        onChange={this.handleChange} disabled />
                    </div>
                  </div>
                  <div className="form-group row">
                    <label className="col-4 align-middle">Points</label>
                    <div className="col">
                      <input type="text" name="points" className="form-control col" value={this.state.points}
                        onChange={this.handleChange} disabled />
                    </div>
                  </div>

                  <div id="save-changes-div">
                    <Button variant="primary" id="save-changes" type="submit">Save changes</Button>
                  </div>

                </form>
              </div>
            </div>
          </div>

        </div>
      </div>


    );
  }
}